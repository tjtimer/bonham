import riot from "riot"

import { validEmail, validPassword } from "../validation"
import * as la from "../actions/auth"
import '../../forms/components/inputs/password'
import '../../forms/components/inputs/email'
import '../../forms/components/buttons/submit'

export default riot.tag(
    "sign-up-form",
    `
    <email-input
        label="Email"
        value="{email}"
        onkeyup="{ changeEmail }"
        valid="{ (emailIsValid) }"></email-input>
    <password-input
        label="Password"
        value="{password}"
        onkeyup="{ changePassword }"
        valid="{ (passwordIsValid) }"></password-input>
    <password-input
        label="Password again"
        value="{password2}"
        onkeyup="{ changePassword2 }"
        valid="{ (password2IsValid) }"></password-input>
    `,
    function(opts) {
        this.email= ""
        this.password = ""
        this.password2 = ""
        this.emailIsValid = false
        this.passwordIsValid = false
        this.password2IsValid = false
        this.parentSignUpIsValid = false
        this.checkValidity = ()=> {
            this.emailIsValid = validEmail(this.email)
            this.passwordIsValid = validPassword(this.password)
            this.password2IsValid = this.password === this.password2
            this.parentSignUpIsValid = this.parent.signUpIsValid
            if (this.emailIsValid && this.passwordIsValid && this.password2IsValid) {
                this.parent.signUpIsValid = true
            } else {
                this.parent.signUpIsValid = false
            }
            if (this.parentSignUpIsValid !== this.parent.signUpIsValid) {
                this.parent.update()
            }
        }
        this.changeEmail = (e) => {
            console.log(this, this[e.target.name])
            this.email = e.target.value
            this.checkValidity()
            if (e.keyCode == 13 && this.parent.signUpIsValid) {
                opts.store.dispatch(la.submitSignUpForm({email: this.email, password: this.password}))
                this.reset()
            }
        }
        this.changePassword = (e) => {
            this.password = e.target.value
            this.checkValidity()
            if (e.keyCode == 13 && this.parent.signUpIsValid) {
                opts.store.dispatch(la.submitSignUpForm({email: this.email, password: this.password}))
                this.reset()
            }
        }
        this.changePassword2 = (e) => {
            this.password2 = e.target.value
            this.checkValidity()
            if (e.keyCode == 13 && this.parent.signUpIsValid) {
                opts.store.dispatch(la.submitSignUpForm({email: this.email, password: this.password}))
                this.reset()
            }
        }
        this.reset = ()=> {
            this.email= ""
            this.password = ""
            this.password2 = ""
        }
    }
)
