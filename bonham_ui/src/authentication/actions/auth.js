import makeActionCreator from '../../utils/action-creator'

export const SUBMIT_LOGIN_FORM = 'SUBMIT_LOGIN_FORM'
export const submitLoginForm = makeActionCreator(SUBMIT_LOGIN_FORM, 'data')

export const SUBMIT_SIGN_UP_FORM = 'SUBMIT_SIGN_UP_FORM'
export const submitSignUpForm = makeActionCreator(SUBMIT_SIGN_UP_FORM, 'data')

export const SUBMIT_LOGIN_TOKEN = 'SUBMIT_LOGIN_TOKEN'
export const submitLoginToken = makeActionCreator(SUBMIT_LOGIN_TOKEN, 'token')

export const SUBMIT_LOGOUT = 'SUBMIT_LOGOUT'
export const submitLogout = makeActionCreator(SUBMIT_LOGOUT, 'token')

export const AUTHENTICATION_REQUEST_SENT = 'AUTHENTICATION_REQUEST_SENT'
export const authRequestSent = makeActionCreator(AUTHENTICATION_REQUEST_SENT)

export const AUTHENTICATION_REQUEST_SUCCESS = 'AUTHENTICATION_REQUEST_SUCCESS'
export const authRequestSuccess = makeActionCreator(AUTHENTICATION_REQUEST_SUCCESS, 'reponse')

export const AUTHENTICATION_REQUEST_ERROR = 'AUTHENTICATION_REQUEST_ERROR'
export const authRequestError = makeActionCreator(AUTHENTICATION_REQUEST_ERROR, 'data')

export const LOG_OUT_SUCCESS = 'LOG_OUT_SUCCESS'
export const logOutSuccess = makeActionCreator(LOG_OUT_SUCCESS)

export const TOGGLE_AUTHENTICATION_FORM = 'TOGGLE_AUTHENTICATION_FORM'
export const toggleAuthForm = makeActionCreator(TOGGLE_AUTHENTICATION_FORM)
