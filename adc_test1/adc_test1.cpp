#include <stdio.h>
#include "pico/stdlib.h"
#include "hardware/adc.h"

// Pin donde conectas tu LED cualquiera (por ejemplo GPIO 15)
#define LED_PIN 15

// Pin para lectura ADC A0 (GPIO 26 corresponde al Canal ADC 0)
#define ADC_A0_GPIO_PIN 26
#define ADC_A0_INPUT_CHANNEL 0

// Factor de conversión para 12 bits de resolución (0 a 4095 -> 0V a 3.3V)
#define ADC_CONVERSION_FACTOR (3.3f / (1 << 12))

int main()
{
    // Inicializar entrada/salida estándar (USB Serial)
    stdio_init_all();

    // 1. Configurar el pin del LED (GPIO 15) como SALIDA
    gpio_init(LED_PIN);
    gpio_set_dir(LED_PIN, GPIO_OUT);

    // 2. Inicializar el módulo ADC y configurar la entrada A0 (GPIO 26)
    adc_init();
    adc_gpio_init(ADC_A0_GPIO_PIN);
    adc_select_input(ADC_A0_INPUT_CHANNEL);

    bool led_state = false;

    while (true) {
        // Alternar estado del LED
        led_state = !led_state;

        // Encender (true / 1) o Apagar (false / 0) el LED en el pin elegido
        gpio_put(LED_PIN, led_state);

        // Leer valor analógico del canal 0 (A0 / GPIO 26)
        // El ADC de la Pico entrega un valor entre 0 y 4095 (12 bits)
        uint16_t raw_value = adc_read();
        float voltage = raw_value * ADC_CONVERSION_FACTOR;

        // Imprimir resultados por USB Serial
        printf("ADC A0 (GPIO 26) -> RAW: %4u | Voltaje: %.3f V | LED (GPIO %d): %s\n",
               raw_value, voltage, LED_PIN, led_state ? "ENCENDIDO" : "APAGADO");

        // Pausa de 500 ms
        sleep_ms(500);
    }

    return 0;
}
