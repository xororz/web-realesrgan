#include <stdint.h>
#include <stdbool.h>

// Usage - generate js and wasm files
// emcc imghelper.c -o imghelper.js -O2 -s WASM=1 -s EXPORTED_FUNCTIONS="['_copy_alpha_to_rgb','_check_alpha','_copy_alpha_channel','_malloc','_free']" -s EXPORTED_RUNTIME_METHODS="['ccall', 'cwrap']" -s ALLOW_MEMORY_GROWTH=1 -s MODULARIZE=1 -s EXPORT_ES6=1

bool check_alpha(uint8_t *data, int pixelCount)
{
    for (int i = 0; i < pixelCount; ++i)
    {
        if (data[i * 4 + 3] != 255)
        {
            return true;
        }
    }
    return false;
}

void copy_alpha_to_rgb(uint8_t *source, uint8_t *target, int pixelCount)
{
    for (int i = 0; i < pixelCount; ++i)
    {
        uint8_t alpha = source[i * 4 + 3];
        target[i * 4 + 0] = alpha;
        target[i * 4 + 1] = alpha;
        target[i * 4 + 2] = alpha;
        target[i * 4 + 3] = alpha;
    }
}

void copy_alpha_channel(uint8_t *source, uint8_t *target, int pixelCount)
{
    for (int i = 0; i < pixelCount; ++i)
    {
        uint8_t alpha = source[i * 4];
        target[i * 4 + 3] = alpha;
    }
}