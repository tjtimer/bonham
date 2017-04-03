import { combineReducers } from 'redux'

import application from './reducers/application'
import modal from './reducers/modal'

export default combineReducers({
    application,
    modal
})
