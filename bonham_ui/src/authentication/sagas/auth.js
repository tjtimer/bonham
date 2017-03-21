import axios from 'axios'
import route from 'riot-route'
import { call, spawn, take, put } from 'redux-saga/effects'
import jwt_decode from 'jwt-decode'
import * as aa from '../actions/auth'

const ls = window.localStorage

const api = axios.create({
    baseURL: 'https://tjtimer.dev/auth/',
    timeout: 10000,
    withCredentials: true,
    responseType: 'json'
})

function* onLoginSuccess(token, user) {
    api.defaults.headers['AUTH-TOKEN'] = token
    ls.setItem('auth-token', token)
    const decoded = jwt_decode(token)
    console.log("got token: ", decoded)
    // yield put(ua.initUser(user))
    // yield put(push(`${decoded.name}/`))
}


function* processSignUp(data) {
    try {
        const response = yield call(api.post, 'sign-up/', data)
        yield put(aa.authRequestSuccess(response))
    } catch (error) {
        yield put(aa.authRequestError(error))
    }
}
function* processLogin(data) {
    try {
        const response = yield call(api.put, 'login/', data)
        yield put(aa.authRequestSuccess(response))
        yield spawn(onLoginSuccess, response.headers['auth-token'], response.data.user)
    } catch (error) {
        console.log(error)
        yield put(aa.authRequestError(error.response.data.message))
    }
}
function* processTokenLogin(token) {
    try {
        api.defaults.headers['AUTH-TOKEN'] = token
        const response = yield call(api.put, 'token-login/')
        yield put(aa.authRequestSuccess(response))
        yield spawn(onLoginSuccess, response.headers['auth-token'], response.data.user)
    } catch(error) {
        ls.removeItem('auth-token')
        yield put(aa.authRequestError(error.response.data.message))
    }
}
function* processLogout(token) {
    try {
        const response = yield call(api.put, 'logout/')
        delete api.defaults.headers['AUTH-TOKEN']
        ls.removeItem('auth-token')
        yield put(aa.authRequestSuccess(response))
    } catch (error) {
        yield put(aa.authRequestError(error))
    }
}
export function* loginFlow() {
    while (true) {
        const login = yield take([aa.SUBMIT_LOGIN_FORM, aa.LOGIN_WITH_TOKEN])
        yield put(aa.authRequestSent())
        if (login.type === 'SUBMIT_LOGIN_FORM'){
            yield spawn(processLogin, login.data)
        } else {
            yield spawn(processTokenLogin, login.token)
        }
        const logout = yield take(aa.SUBMIT_LOGOUT)
        yield put(aa.authRequestSent())
        yield spawn(processLogout, logout.token)
    }
}
export function* signUpFlow() {
    while (true) {
        const signUp = yield take(aa.SUBMIT_SIGN_UP_FORM)
        yield put(aa.authRequestSent())
        yield spawn(processSignUp, signUp.data)
        const logout = yield take(aa.SUBMIT_LOGOUT)
        yield put(aa.authRequestSent())
        yield spawn(processLogout, logout.token)
    }
}
export default function* authSaga() {
    yield [
        spawn(loginFlow),
        spawn(signUpFlow)
    ]
}
