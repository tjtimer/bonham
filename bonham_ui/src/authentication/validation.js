export function validEmail(value) {
    try {
        const [name, domain] = value.split('@')
        const [host, tld] = domain.split('.')
        const parts = name.split('.').concat([host, tld])
        if (host.length && tld.length >= 2) {
            for (let part of parts) {
                const has_special_chars = part.match(/\W/)
                if (has_special_chars === '-' || has_special_chars === null)
                    return true
            }
        }
        return false
    } catch(e) {
        return false
    }
}
export function validPassword(value) {
    const has_special_chars = value.match(/\W/g)
    const has_digits = value.match(/\d/g)
    const has_uppercase_letters = value.match(/[A-Z]/g)
    const has_lowercase_letters = value.match(/[a-z]/g)
    const has_whitespaces = value.match(/\s/g)
    if (has_special_chars && has_digits && has_lowercase_letters && has_uppercase_letters && !has_whitespaces)
        return true
    return false
}
