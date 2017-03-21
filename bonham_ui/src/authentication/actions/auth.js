import makeActionCreator from '../../utils'

export const SUBMIT_LOGIN_FORM = 'SUBMIT_LOGIN_FORM'
export const submitLoginForm = makeActionCreator(SUBMIT_LOGIN_FORM, 'data')

export const SUBMIT_SIGN_UP_FORM = 'SUBMIT_SIGN_UP_FORM'
export const submitSignUpForm = makeActionCreator(SUBMIT_SIGN_UP_FORM, 'data')

export const LOGIN_WITH_TOKEN = 'LOGIN_WITH_TOKEN'
export const loginWithToken = makeActionCreator(LOGIN_WITH_TOKEN, 'token')

export const SUBMIT_LOGOUT = 'SUBMIT_LOGOUT'
export const submitLogout = makeActionCreator(SUBMIT_LOGOUT, 'token')

export const AUTH_REQUEST_SENT = 'AUTH_REQUEST_SENT'
export const authRequestSent = makeActionCreator(AUTH_REQUEST_SENT)

export const AUTH_REQUEST_SUCCESS = 'AUTH_REQUEST_SUCCESS'
export const authRequestSuccess = makeActionCreator(AUTH_REQUEST_SUCCESS, 'data')

export const AUTH_REQUEST_ERROR = 'AUTH_REQUEST_ERROR'
export const authRequestError = makeActionCreator(AUTH_REQUEST_ERROR, 'data')

// export const LOGOUT_REQUEST_SENT = 'LOGOUT_REQUEST_SENT'
// export const logoutRequestSent = makeActionCreator(LOGOUT_REQUEST_SENT)
//
// export const LOGOUT_REQUEST_SUCCESS = 'LOGOUT_REQUEST_SUCCESS'
// export const logoutRequestSuccess = makeActionCreator(LOGOUT_REQUEST_SUCCESS, 'data')
//
// export const LOGOUT_REQUEST_ERROR = 'LOGOUT_REQUEST_ERROR'
// export const logoutRequestError = makeActionCreator(LOGOUT_REQUEST_ERROR, 'data')
