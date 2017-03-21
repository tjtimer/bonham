import { combineReducers } from 'redux'

import core from './core/reducer'
import auth from './authentication/reducers/auth'

export default combineReducers(
    {
        core,
        auth
    }
)
