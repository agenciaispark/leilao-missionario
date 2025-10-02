import * as React from "react"

const TOAST_LIMIT = 1
const TOAST_REMOVE_DELAY = 1000000

const actionTypes = {
  ADD_TOAST: "ADD_TOAST",
  UPDATE_TOAST: "UPDATE_TOAST",
  DISMISS_TOAST: "DISMISS_TOAST",
  REMOVE_TOAST: "REMOVE_TOAST",
}

let count = 0

function genId() {
  count = (count + 1) % Number.MAX_VALUE
  return count.toString()
}

function toastTime(duration) {
  return duration === null ? TOAST_REMOVE_DELAY : duration
}

const reducer = (state, action) => {
  switch (action.type) {
    case actionTypes.ADD_TOAST:
      return {
        ...state,
        toasts: [action.toast, ...state.toasts].slice(0, TOAST_LIMIT),
      }

    case actionTypes.UPDATE_TOAST:
      return {
        ...state,
        toasts: state.toasts.map((t) =>
          t.id === action.toast.id ? { ...t, ...action.toast } : t
        ),
      }

    case actionTypes.DISMISS_TOAST:
      const { toastId } = action

      // ! Side effects ! - This means all toasts are completely removed after the timeout for performance reasons.
      // We are doing this to avoid a memory leak with the toast object for long running apps.
      const toasts = state.toasts.map((t) =>
        t.id === toastId || toastId === undefined
          ? {
              ...t,
              open: false,
            }
          : t
      )

      return { ...state, toasts }

    case actionTypes.REMOVE_TOAST:
      const { toastId: removeToastId } = action

      return {
        ...state,
        toasts: state.toasts.filter((t) => t.id !== removeToastId),
      }
    default:
      return state
  }
}

const listeners = []

let memoryState = { toasts: [] }

function dispatch(action) {
  memoryState = reducer(memoryState, action)
  listeners.forEach((listener) => {
    listener(memoryState)
  })
}

function bind(listener) {
  listeners.push(listener)
  return function unsubscribe() {
    const index = listeners.indexOf(listener)
    if (index > -1) {
      listeners.splice(index, 1)
    }
  }
}

function useToast() {
  const [state, setState] = React.useState(memoryState)

  React.useEffect(() => {
    return bind(setState)
  }, [state])

  return {
    ...state,
    toast: React.useCallback(({ ...props }) => {
      const id = genId()
      const update = (props) => dispatch({ type: actionTypes.UPDATE_TOAST, toast: { ...props, id } })
      const dismiss = () => dispatch({ type: actionTypes.DISMISS_TOAST, toastId: id })
      dispatch({ type: actionTypes.ADD_TOAST, toast: { ...props, id, open: true, update, dismiss } })
      return { id, update, dismiss }
    }, []),
  }
}

export { useToast, reducer as toastReducer }

