import { combineReducers } from 'redux'

import core from './core/reducer'
import auth from './authentication/reducers/auth'
import account from './authentication/reducers/account'

export default combineReducers(
    {
        core,
        auth,
        account
    }
)
