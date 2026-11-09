import { flushPromises, shallowMount } from '@vue/test-utils'
import { beforeEach, describe, expect, it, vi } from 'vitest'

import ChatComponent from '../components/ChatComponent.vue'

const { messagesCreate } = vi.hoisted(() => ({ messagesCreate: vi.fn() }))

vi.mock('@/api-client', () => ({
  Configuration: class {},
  MessagesApi: class {
    messagesCreate = messagesCreate
  },
}))

describe('ChatComponent', () => {
  beforeEach(() => {
    messagesCreate.mockReset()
    messagesCreate.mockResolvedValue({ response: 'Answer', ward: '渋谷' })
    Element.prototype.scrollTo = vi.fn()
  })

  it('sends a message and displays the response and ward', async () => {
    const wrapper = shallowMount(ChatComponent, {
      global: {
        renderStubDefaultSlot: true,
        stubs: {
          Textarea: {
            props: ['modelValue'],
            emits: ['update:modelValue', 'keydown'],
            template:
              '<textarea :value="modelValue" @input="$emit(\'update:modelValue\', $event.target.value)" @keydown="$emit(\'keydown\', $event)" />',
          },
        },
      },
    })
    await wrapper.get('textarea').setValue('Question')
    await wrapper.get('textarea').trigger('keydown', { key: 'Enter' })
    await flushPromises()

    expect(messagesCreate).toHaveBeenCalledWith({
      messageRequest: {
        message: 'Question',
        lat: undefined,
        lon: undefined,
        isPoint: undefined,
        language: 'en',
      },
    })
    expect(wrapper.emitted('wardChange')).toEqual([[null], ['渋谷']])
    expect(
      wrapper.findAllComponents({ name: 'ChatMessageComponent' })[1]?.props('message'),
    ).toMatchObject({
      role: 'agent',
      content: 'Answer',
    })
  })

  it('sends map coordinates with the localized question', async () => {
    const wrapper = shallowMount(ChatComponent, { global: { renderStubDefaultSlot: true } })
    wrapper.vm.sendMapQuery({ lat: 35, lon: 139, isPoint: true })
    await flushPromises()

    expect(messagesCreate).toHaveBeenCalledWith({
      messageRequest: {
        message: 'Tell me about this location.',
        lat: 35,
        lon: 139,
        isPoint: true,
        language: 'en',
      },
    })
    expect(wrapper.emitted('wardChange')).toEqual([[null], ['渋谷']])
  })
})
