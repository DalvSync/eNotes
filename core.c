#include <sodium.h>
#include <stdlib.h>
#include <string.h>
#include <stdint.h>

#define SALT_LEN crypto_pwhash_SALTBYTES       
#define NONCE_LEN crypto_secretbox_NONCEBYTES  
#define MAC_LEN crypto_secretbox_MACBYTES     
#define KEY_LEN crypto_secretbox_KEYBYTES    

int enotes_encrypt(const uint8_t *data, size_t data_len, const char *password, uint8_t **out_buffer, size_t *out_len) {
    if (sodium_init() < 0) return -1;

    *out_len = SALT_LEN + NONCE_LEN + data_len + MAC_LEN;
    *out_buffer = (uint8_t *)malloc(*out_len);
    if (*out_buffer == NULL) return -2;

    uint8_t salt[SALT_LEN];
    uint8_t nonce[NONCE_LEN];
    uint8_t key[KEY_LEN];

    randombytes_buf(salt, SALT_LEN);
    randombytes_buf(nonce, NONCE_LEN);

    if (crypto_pwhash(key, KEY_LEN, password, strlen(password), salt,
                      crypto_pwhash_OPSLIMIT_INTERACTIVE,
                      crypto_pwhash_MEMLIMIT_INTERACTIVE,
                      crypto_pwhash_ALG_DEFAULT) != 0) {
        free(*out_buffer);
        return -3;
    }

    uint8_t *out_salt = *out_buffer;
    uint8_t *out_nonce = *out_buffer + SALT_LEN;
    uint8_t *out_ct = *out_buffer + SALT_LEN + NONCE_LEN;

    memcpy(out_salt, salt, SALT_LEN);
    memcpy(out_nonce, nonce, NONCE_LEN);

    crypto_secretbox_easy(out_ct, data, data_len, nonce, key);

    sodium_memzero(key, KEY_LEN);

    return 0;
}

int enotes_decrypt(const uint8_t *blob, size_t blob_len, const char *password, uint8_t **out_buffer, size_t *out_len) {
    if (sodium_init() < 0) return -1;

    if (blob_len < SALT_LEN + NONCE_LEN + MAC_LEN) return -4;

    const uint8_t *salt = blob;
    const uint8_t *nonce = blob + SALT_LEN;
    const uint8_t *ct = blob + SALT_LEN + NONCE_LEN;
    size_t ct_len = blob_len - SALT_LEN - NONCE_LEN;

    *out_len = ct_len - MAC_LEN;
    *out_buffer = (uint8_t *)malloc(*out_len);
    if (*out_buffer == NULL) return -2;

    uint8_t key[KEY_LEN];
    if (crypto_pwhash(key, KEY_LEN, password, strlen(password), salt,
                      crypto_pwhash_OPSLIMIT_INTERACTIVE,
                      crypto_pwhash_MEMLIMIT_INTERACTIVE,
                      crypto_pwhash_ALG_DEFAULT) != 0) {
        free(*out_buffer);
        return -3;
    }

    if (crypto_secretbox_open_easy(*out_buffer, ct, ct_len, nonce, key) != 0) {
        sodium_memzero(key, KEY_LEN);
        free(*out_buffer);
        return -5;
    }

    sodium_memzero(key, KEY_LEN);
    return 0;
}

void enotes_free(uint8_t *buffer, size_t len) {
    if (buffer != NULL) {
        sodium_memzero(buffer, len);
        free(buffer);
    }
}