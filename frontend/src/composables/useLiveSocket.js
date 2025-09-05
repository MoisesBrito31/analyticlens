import { ref, onMounted, onBeforeUnmount } from 'vue'
import { io } from 'socket.io-client'

export function useLiveSocket(url, options = {}) {
  const socket = ref(null)
  const connected = ref(false)
  const lastEvent = ref(null)

  function connect() {
    if (socket.value) return
    const s = io(url, { transports: ['websocket'], autoConnect: true, reconnection: true, reconnectionAttempts: 10, reconnectionDelay: 500, ...options })
    socket.value = s
    s.on('connect', () => { connected.value = true; options.onConnectState?.(true) })
    s.on('disconnect', () => { connected.value = false; options.onConnectState?.(false) })
    s.on('test_result', (payload) => { lastEvent.value = payload; options.onResult?.(payload) })
  }

  function disconnect() {
    if (!socket.value) return
    socket.value.disconnect()
    socket.value = null
  }

  onMounted(connect)
  onBeforeUnmount(disconnect)

  return { socket, connected, lastEvent, connect, disconnect }
}
