import * as aa from '../actions/auth'

const initialState = {
    isAuthenticated: false,
    isAuthenticating: false,
    showLogin: true
}

export default function(state=initialState, action) {
    switch (action.type) {
        case aa.AUTHENTICATION_REQUEST_SENT:
            return {
                ...state,
                isAuthenticating: true
            }
        case aa.AUTHENTICATION_REQUEST_SUCCESS:
            return {
                ...state,
                isAuthenticated: true,
                isAuthenticating: false,
            }
        case aa.AUTHENTICATION_REQUEST_ERROR:
            return {
                ...state,
                isAuthenticated: false,
                isAuthenticating: false
            }
        case aa.LOG_OUT_SUCCESS:
            return {
                ...state,
                isAuthenticated: false,
                isAuthenticating: false
            }
        case aa.TOGGLE_AUTHENTICATION_FORM:
            return {
                ...state,
                showLogin: !state.showLogin
            }
        default:
            return state
    }
}
