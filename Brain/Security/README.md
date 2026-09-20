# BPFCo Security Architecture

Normal external approval requires:
1. Human terminal interaction.
2. Registered BPFCo USB token present.
3. Brain ID/token binding verified.
4. Cryptographic token validation succeeds.
5. Human presses Enter.

The USB key is a software cryptographic token on removable media. It is NOT represented as a hardware security module.

Recovery is deliberately different:
- Recovery password is PBKDF2-HMAC-SHA256 protected.
- Recovery cannot directly become a permanent approval bypass.
- Recovery is used to revoke/rotate the lost token and issue a new token.
- Normal approval remains USB-required after recovery.

Future upgrade:
Replace the removable-media token with a true hardware cryptographic token without changing Fred's approval workflow.

Secrets:
- Private token secret is never committed to Git.
- Git stores only the Brain identity, token identifier, binding hash and password verifier.
