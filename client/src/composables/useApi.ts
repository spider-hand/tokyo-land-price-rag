import { Configuration } from '@/api-client'

const useApi = () => {
  const apiConfig = new Configuration({
    basePath: '',
  })

  return { apiConfig }
}

export default useApi
