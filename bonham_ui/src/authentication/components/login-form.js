import riot from 'riot'

import { validEmail, validPassword } from '../validation'
import * as la from '../actions/auth'

export default riot.tag(
    'login-form',
    `
        <label>Email</label>
        <input
            type="email"
            onkeyup="{ changeEmail }"
            placeholder="email"
            class="{ (emailIsValid) ? 'valid' : 'invalid' }" />

        <label>Password</label>
        <input
            type="password"
            onkeyup="{ changePassword }"
            class="{ (passwordIsValid) ? 'valid' : 'invalid' }" />
        <input
            type="button"
            onclick="{ submit }"
            value="submit"
            disabled="{ (emailIsValid && passwordIsValid) ? false : true }" />
    `,
    function(opts) {
        this.email= ""
        this.password = ""
        this.emailIsValid = false
        this.passwordIsValid = false
        this.changeEmail = (e) => {
            const v = e.target.value
            if (v.length >= 3) {
                if (validEmail(v)) {
                    this.emailIsValid = true
                    this.email = v
                }
            }
        }
        this.changePassword = (e) => {
            const v = e.target.value
            if (v.length >= 8) {
                if (validPassword(v)) {
                    this.passwordIsValid = true
                    this.password = v
                    if (e.keyCode == 13) {
                        opts.store.dispatch(la.submitLoginForm({email: this.email, password: this.password}))
                    }
                }
            }
        }
        this.submit = ()=> {
            opts.store.dispatch(la.submitLoginForm({email: this.email, password: this.password}))
        }
    }
)
