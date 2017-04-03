import route from 'riot-route'
import { call, spawn, take, takeEvery, put } from 'redux-saga/effects'
import jwt_decode from 'jwt-decode'
import api from '../../core/api'
import * as authentication_actions from '../actions/auth'

const ls = window.localStorage

function *handleError(error) {
    yield put(authentication_actions.authRequestError(error.response))
    delete api.defaults.headers['AUTH-TOKEN']
    ls.removeItem('auth-token')
}
function* processLogout(token) {
    yield put(authentication_actions.authRequestSent())
    try {
        const response = yield call(api.put, 'auth/logout/')
        delete api.defaults.headers['AUTH-TOKEN']
        ls.removeItem('auth-token')
        yield put(authentication_actions.logOutSuccess())
    } catch (error) {
        yield spawn(handleError, error)
    }
}
function* handleSuccess(response) {
    const token = response.headers['auth-token']
    api.defaults.headers['AUTH-TOKEN'] = token
    ls.setItem('auth-token', token)
    yield put(authentication_actions.authRequestSuccess(response))
    const logout = yield take(authentication_actions.SUBMIT_LOGOUT)
    yield spawn(processLogout, logout.token)
}


function* processSignUp(data) {
    try {
        const response = yield call(api.post, 'auth/sign-up/', data)
        yield spawn(handleSuccess, response)
    } catch (error) {
        yield spawn(handleError, error)
    }
}
function* processLogin(data) {
    try {
        const response = yield call(api.put, 'auth/login/', data)
        yield spawn(handleSuccess, response)
    } catch (error) {
        yield spawn(handleError, error)
    }
}
function* processTokenLogin(token) {
    try {
        api.defaults.headers['AUTH-TOKEN'] = token
        const response = yield call(api.put, 'auth/token-login/')
        yield spawn(handleSuccess, response)
    } catch(error) {
        yield spawn(handleError, error)
    }
}

export default function* authSaga() {
    while (true) {
        const request = yield take([authentication_actions.SUBMIT_SIGN_UP_FORM, authentication_actions.SUBMIT_LOGIN_FORM, authentication_actions.SUBMIT_LOGIN_TOKEN])
        yield put(authentication_actions.authRequestSent())
        if (request.type === 'SUBMIT_SIGN_UP_FORM') {
            yield spawn(processSignUp, request.data)
        } else if (request.type === 'SUBMIT_LOGIN_FORM') {
            yield spawn(processLogin, request.data)
        } else {
            yield spawn(processTokenLogin, request.token)
        }
    }
}
