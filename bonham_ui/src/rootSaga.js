import authSaga from './authentication/saga'

export default function *rootSaga() {
    yield [
        authSaga(),
    ]
}
