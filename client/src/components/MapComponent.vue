<template>
  <div class="relative h-full w-full">
    <div ref="mapContainer" class="h-full w-full" />
    <div class="bg-background absolute bottom-4 left-4 rounded-lg p-2 shadow-lg">
      <div class="flex items-end gap-2 px-2 mb-1">
        <div class="font-semibold">{{ t.landPriceIn2025 }}</div>
        <div class="text-sm">({{ t.jpyPerSquareMeter }})</div>
      </div>
      <ItemGroup>
        <Item v-for="(item, index) in legendItems" :key="index" class="flex items-center px-2 py-1">
          <div class="h-2 w-2 rounded-full" :style="{ backgroundColor: item.color }" />
          <span>{{ item.label }}</span>
        </Item>
      </ItemGroup>
    </div>
  </div>
</template>

<script setup lang="ts">
import { onMounted, onUnmounted, ref, computed } from 'vue'
import maplibregl from 'maplibre-gl'
import 'maplibre-gl/dist/maplibre-gl.css'
import * as pmtiles from 'pmtiles'
import ItemGroup from './ui/item/ItemGroup.vue'
import Item from './ui/item/Item.vue'
import useLanguage from '@/composables/useLanguage'

export interface MapClickEvent {
  lat: number
  lon: number
  isPoint: boolean
  address?: string
}

const emit = defineEmits<{
  mapClick: [event: MapClickEvent]
}>()

const { t } = useLanguage()

const COLOR_PALETTE = [
  'rgb(153, 102, 255)',
  'rgb(54, 162, 235)',
  'rgb(75, 192, 192)',
  'rgb(255, 205, 86)',
  'rgb(255, 159, 64)',
  'rgb(255, 99, 132)',
]

const legendItems = computed(() => [
  { color: COLOR_PALETTE[5], label: `${t.value.top} 1% (> ¥17,287,000)` },
  { color: COLOR_PALETTE[4], label: `${t.value.top} 10% (¥2,520,000 - ¥17,287,000)` },
  { color: COLOR_PALETTE[3], label: `${t.value.top} 50% (¥514,500 - ¥2,520,000)` },
  { color: COLOR_PALETTE[2], label: `${t.value.bottom} 50% (¥149,000 - ¥514,500)` },
  { color: COLOR_PALETTE[1], label: `${t.value.bottom} 10% (¥35,590 - ¥149,000)` },
  { color: COLOR_PALETTE[0], label: `${t.value.bottom} 1% (< ¥35,590)` },
])

const WARD_CENTERS: Record<string, [number, number]> = {
  あきる野: [139.2254, 35.7328],
  三宅: [139.5211, 34.0851],
  三鷹: [139.5604, 35.6847],
  世田谷: [139.6351, 35.6397],
  中央: [139.7772, 35.6711],
  中野: [139.6625, 35.7109],
  八丈: [139.7979, 33.1064],
  八王子: [139.2877, 35.6598],
  利島: [139.2792, 34.5224],
  北: [139.7289, 35.7659],
  千代田: [139.7546, 35.6877],
  台東: [139.786, 35.7155],
  品川: [139.7255, 35.6116],
  国分寺: [139.4612, 35.7055],
  国立: [139.4388, 35.6863],
  墨田: [139.8155, 35.7122],
  多摩: [139.4399, 35.6306],
  大島: [139.3988, 34.7375],
  大田: [139.7275, 35.5675],
  奥多摩: [139.0555, 35.8226],
  小平: [139.4817, 35.7274],
  小笠原: [142.1557, 26.6672],
  小金井: [139.511, 35.7011],
  府中: [139.4832, 35.6705],
  御蔵島: [139.6032, 33.8749],
  文京: [139.7473, 35.7175],
  新宿: [139.709, 35.7011],
  新島: [139.2114, 34.3254],
  日の出: [139.2264, 35.7587],
  日野: [139.3986, 35.6633],
  昭島: [139.3642, 35.7078],
  杉並: [139.6254, 35.6968],
  東久留米: [139.5199, 35.7539],
  東大和: [139.4266, 35.7503],
  東村山: [139.4724, 35.7592],
  板橋: [139.6765, 35.7726],
  檜原: [139.1045, 35.725],
  武蔵村山: [139.3839, 35.7504],
  武蔵野: [139.5616, 35.7081],
  江戸川: [139.8757, 35.6926],
  江東: [139.8167, 35.6659],
  清瀬: [139.5222, 35.7814],
  渋谷: [139.6963, 35.6679],
  港: [139.7379, 35.653],
  狛江: [139.5772, 35.6349],
  瑞穂: [139.3493, 35.7743],
  町田: [139.4304, 35.5761],
  目黒: [139.6882, 35.63],
  神津島: [139.1479, 34.2145],
  福生: [139.3364, 35.736],
  稲城: [139.4929, 35.6329],
  立川: [139.4045, 35.7145],
  練馬: [139.6177, 35.7478],
  羽村: [139.3154, 35.764],
  荒川: [139.7813, 35.7399],
  葛飾: [139.8557, 35.7532],
  西東京: [139.5462, 35.7349],
  調布: [139.5522, 35.6577],
  豊島: [139.7116, 35.7315],
  足立: [139.7951, 35.7788],
  青ヶ島: [139.7665, 32.4574],
  青梅: [139.242, 35.8036],
}

const mapContainer = ref<HTMLElement | null>(null)
let map: maplibregl.Map | null = null

const protocol = new pmtiles.Protocol()
maplibregl.addProtocol('pmtiles', protocol.tile)

onMounted(() => {
  if (mapContainer.value) {
    map = new maplibregl.Map({
      container: mapContainer.value,
      style: {
        version: 8,
        sources: {
          'raster-tiles': {
            type: 'raster',
            tiles: [
              `https://api.mapbox.com/styles/v1/mapbox/streets-v12/tiles/{z}/{x}/{y}?access_token=${import.meta.env.VITE_MAPBOX_TOKEN}`,
            ],
            tileSize: 512,
            attribution:
              '© <a href="https://www.mapbox.com/about/maps/">Mapbox</a> © <a href="http://www.openstreetmap.org/copyright">OpenStreetMap</a> <strong><a href="https://www.mapbox.com/map-feedback/" target="_blank">Improve this map</a></strong>',
          },
        },
        layers: [
          {
            id: 'raster-tiles-layer',
            type: 'raster',
            source: 'raster-tiles',
          },
        ],
      },
      center: [139.5803, 35.7023],
      zoom: 10,
      minZoom: 10,
      maxZoom: 16,
      maxBounds: [
        [138.8, 35.4],
        [140.1, 35.95],
      ],
    })

    map.on('load', () => {
      map!.addSource('wards', {
        type: 'vector',
        url: import.meta.env.VITE_WARDS_PMTILES_URL,
      })

      map!.addLayer({
        id: 'wards-layer',
        type: 'fill',
        source: 'wards',
        'source-layer': 'district',
        paint: {
          'fill-color': '#000000',
          'fill-opacity': 0,
          'fill-outline-color': '#000000',
        },
      })

      map!.addLayer({
        id: 'wards-highlight',
        type: 'line',
        source: 'wards',
        'source-layer': 'district',
        filter: ['==', ['slice', ['get', 'N03_004'], 0, -1], ''],
        paint: {
          'line-color': 'rgb(255, 99, 132)',
          'line-width': 4,
          'line-opacity': 0.8,
        },
      })

      map!.addSource('land-price', {
        type: 'vector',
        url: import.meta.env.VITE_LAND_PRICE_PMTILES_URL,
      })

      map!.addLayer({
        id: 'land-price-layer',
        type: 'circle',
        source: 'land-price',
        'source-layer': 'L0125_13',
        paint: {
          'circle-radius': 5,
          'circle-color': [
            'step',
            ['get', 'L01_008'],
            COLOR_PALETTE[0] as string,
            35590,
            COLOR_PALETTE[1] as string,
            149000,
            COLOR_PALETTE[2] as string,
            514500,
            COLOR_PALETTE[3] as string,
            2520000,
            COLOR_PALETTE[4] as string,
            17287000,
            COLOR_PALETTE[5] as string,
          ],
          'circle-opacity': 0.8,
          'circle-stroke-width': 1,
          'circle-stroke-color': '#ffffff',
          'circle-stroke-opacity': 0.2,
        },
      })

      map!.on('mouseenter', 'land-price-layer', () => {
        map!.getCanvas().style.cursor = 'pointer'
      })

      map!.on('mouseleave', 'land-price-layer', () => {
        map!.getCanvas().style.cursor = ''
      })

      map!.on('click', (e) => {
        const features = map!.queryRenderedFeatures(e.point, {
          layers: ['land-price-layer'],
        })

        if (features.length > 0) {
          // Handle click on a point feature
          const feature = features[0]!
          const geometry = feature.geometry as GeoJSON.Point
          const coordinates = geometry.coordinates
          emit('mapClick', {
            lat: coordinates[1] as number,
            lon: coordinates[0] as number,
            isPoint: true,
            address: feature.properties?.L01_025 as string | undefined,
          })
        } else {
          // Handle click on a non-feature area
          emit('mapClick', {
            lat: e.lngLat.lat,
            lon: e.lngLat.lng,
            isPoint: false,
          })
        }
      })
    })
  }
})

onUnmounted(() => {
  if (map) {
    map.remove()
    map = null
  }
})

const highlightWard = (ward: string | null) => {
  if (!map) return

  if (ward) {
    map.setFilter('wards-highlight', ['==', ['slice', ['get', 'N03_004'], 0, -1], ward])

    const center = WARD_CENTERS[ward]
    if (center) {
      map.flyTo({
        center: center,
        zoom: 12,
        duration: 1500,
      })
    }
  } else {
    map.setFilter('wards-highlight', ['==', ['slice', ['get', 'N03_004'], 0, -1], ''])
  }
}

defineExpose({
  highlightWard,
})
</script>
