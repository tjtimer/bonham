import coreSaga from './core/saga'
import authSaga from './authentication/saga'


export default function *rootSaga() {
    yield [
        coreSaga(),
        authSaga(),
    ]
}
