import * as aa from '../actions/auth'

const initialState = {
    isAuthenticated: false,
    isAuthenticating: false,
    error: ''
}

export default function(state=initialState, action) {
    console.log(action)
    switch (action.type) {
        case aa.AUTH_REQUEST_SENT:
            return {
                ...state,
                isAuthenticating: true
            }
        case aa.AUTH_REQUEST_SUCCESS:
            return {
                ...state,
                isAuthenticated: true,
                isAuthenticating: false,
            }
        case aa.AUTH_REQUEST_ERROR:
            return {
                ...state,
                isAuthenticated: false,
                isAuthenticating: false,
                error: action.data.message
            }
        default:
            return state
    }
}
