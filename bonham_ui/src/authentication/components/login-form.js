import riot from 'riot'

import { validEmail, validPassword } from '../validation'
import * as la from '../actions/auth'
import '../../forms/components/inputs/password'
import '../../forms/components/inputs/email'
import '../../forms/components/buttons/submit'

export default riot.tag(
    'login-form',
    `
            <email-input
                label="Email"
                value="{ email }"
                onkeyup="{ changeEmail }"
                valid="{ (emailIsValid) }"></email-input>
            <password-input
                label="Password"
                value="{ password }"
                onkeyup="{ changePassword }"
                valid="{ (passwordIsValid) }"></password-input>

    `,
    function(opts) {
        this.email= ""
        this.password = ""
        this.emailIsValid = false
        this.passwordIsValid = false
        this.parentLoginIsValid = false
        this.checkValidity = ()=> {
            this.emailIsValid = validEmail(this.email)
            this.passwordIsValid = validPassword(this.password)
            this.parentLoginIsValid = this.parent.loginIsValid
            if (this.emailIsValid && this.passwordIsValid) {
                this.parent.loginIsValid = true
            } else {
                this.parent.loginIsValid = false
            }
            if (this.parentLoginIsValid !== this.parent.loginIsValid) {
                this.parent.update()
            }
        }
        this.changeEmail = (e) => {
            this.email = e.target.value
            this.checkValidity()
            if (e.keyCode == 13 && this.parent.loginIsValid) {
                opts.store.dispatch(la.submitLoginForm({email: this.email, password: this.password}))
                this.reset()
            }
        }
        this.changePassword = (e) => {
            this.password = e.target.value
            this.checkValidity()
            if (e.keyCode == 13 && this.parent.loginIsValid) {
                opts.store.dispatch(la.submitLoginForm({email: this.email, password: this.password}))
                this.reset()
            }
        }
        this.reset = ()=> {
            this.email= ""
            this.password = ""
            this.checkValidity()
        }
    }
)
