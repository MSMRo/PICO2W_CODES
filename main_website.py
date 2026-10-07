from __future__ import annotations

from html import escape

import streamlit as st


st.set_page_config(
    page_title="Pico 2 W | guía de hardware y SDK",
    page_icon=":material/developer_board:",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.html(
    """
    <style>
    .pico-hero {
        padding: 2rem 2.2rem;
        margin: .25rem 0 1.4rem;
        border: 1px solid rgba(230, 43, 83, .23);
        border-radius: 24px;
        background:
            radial-gradient(ellipse at 88% 8%, rgba(255, 92, 122, .23), transparent 34%),
            linear-gradient(130deg, #151d31 0%, #202b42 64%, #3b2035 100%);
        color: #f8fafc;
    }
    .pico-hero .eyebrow {
        color: #ff9caf;
        font-size: .76rem;
        font-weight: 750;
        letter-spacing: .15em;
        text-transform: uppercase;
    }
    .pico-hero h1 {
        margin: .55rem 0;
        color: #fff;
        font-size: clamp(2rem, 4vw, 3.2rem);
        line-height: 1.08;
    }
    .pico-hero p {
        max-width: 760px;
        margin: .5rem 0 0;
        color: #d7deeb;
        font-size: 1.05rem;
        line-height: 1.65;
    }
    .pico-label {
        display: inline-block;
        padding: .25rem .65rem;
        margin: .2rem .3rem .1rem 0;
        border: 1px solid rgba(255, 255, 255, .2);
        border-radius: 999px;
        color: #f7dce3;
        font-size: .78rem;
    }
    .pico-muted {
        color: #667085;
    }
    .pico-code-note {
        padding: .8rem 1rem;
        border-left: 3px solid #d9234f;
        border-radius: 0 10px 10px 0;
        background: rgba(217, 35, 79, .07);
    }
    </style>
    """
)

NAVIGATION = (
    "Inicio",
    "Arquitectura",
    "Periféricos",
    "API del Pico SDK",
    "Wi-Fi y Bluetooth",
    "DSP, SVM y redes neuronales",
    "Compilar y cargar",
)

NAV_ICONS = {
    "Inicio": ":material/home:",
    "Arquitectura": ":material/memory:",
    "Periféricos": ":material/developer_board:",
    "API del Pico SDK": ":material/code:",
    "Wi-Fi y Bluetooth": ":material/wifi:",
    "DSP, SVM y redes neuronales": ":material/neurology:",
    "Compilar y cargar": ":material/build:",
}


PERIPHERALS = {
    "GPIO digital": {
        "group": "Entradas y salidas",
        "description": "Lee botones y controla señales digitales. Usa niveles lógicos de 3.3 V.",
        "theory": "Los GPIO pueden ser entradas, salidas o conectarse a funciones alternativas de los periféricos. La Pico 2 W usa el RP2350A, que implementa 30 GPIO; la placa expone 26 como GPIO de usuario y comparte/reserva señales para funciones internas.",
        "resources": ["30 GPIO en la variante RP2350A; 26 líneas GPIO de usuario expuestas por la Pico 2 W.", "Entrada/salida digital de 3.3 V; cada pin selecciona una función alternativa.", "Pull-up/pull-down, Schmitt trigger, slew rate y drive strength configurables."],
        "api": [
            ("gpio_init / gpio_deinit", "Inicializan o liberan el pin para uso SIO."),
            ("gpio_set_dir / gpio_get_dir", "Configuran o consultan entrada y salida."),
            ("gpio_put / gpio_get", "Escriben o leen el nivel lógico."),
            ("gpio_put_masked / gpio_set_mask / gpio_clr_mask / gpio_xor_mask", "Actualizan uno o varios GPIO con máscaras."),
            ("gpio_pull_up / gpio_pull_down / gpio_disable_pulls", "Configuran resistencias internas de polarización."),
            ("gpio_set_function", "Selecciona GPIO_FUNC_SIO, GPIO_FUNC_I2C, GPIO_FUNC_SPI, GPIO_FUNC_UART, PWM, PIO, etc."),
            ("gpio_set_irq_enabled", "Habilita interrupciones por flanco ascendente/descendente o nivel alto/bajo."),
        ],
        "pins": "Ejemplo: GPIO 15 para salida; GPIO 14 para botón.",
        "library": "pico_stdlib",
        "wire": "LED externo con resistencia en serie entre GPIO y GND. Botón entre GPIO y GND usando pull-up.",
        "warning": "No conectes 5 V a un GPIO. No uses GPIO para alimentar motores o cargas grandes.",
        "code": r'''#include "pico/stdlib.h"

constexpr uint LED_PIN = 15;
constexpr uint BUTTON_PIN = 14;

int main() {
    gpio_init(LED_PIN);
    gpio_set_dir(LED_PIN, GPIO_OUT);

    gpio_init(BUTTON_PIN);
    gpio_set_dir(BUTTON_PIN, GPIO_IN);
    gpio_pull_up(BUTTON_PIN);

    while (true) {
        const bool pulsado = !gpio_get(BUTTON_PIN);
        gpio_put(LED_PIN, pulsado);
        sleep_ms(10);
    }
}''',
    },
    "I2C": {
        "group": "Buses serie",
        "description": "Bus de dos señales con direcciones. Adecuado para sensores, RTCs y expansores.",
        "theory": "I2C usa SDA bidireccional y SCL de reloj, con dispositivos esclavos direccionados. El controlador puede operar como maestro o esclavo; múltiples dispositivos comparten el bus.",
        "resources": ["2 controladores hardware: i2c0 e i2c1.", "Direcciones I2C típicas de 7 bits (algunos dispositivos permiten 10 bits).", "SDA/SCL requieren pull-ups; el SDK configura velocidad solicitada en Hz."],
        "api": [
            ("i2c_init / i2c_deinit", "Inicializan el controlador y solicitan una velocidad de bus."),
            ("i2c_set_baudrate", "Cambia la velocidad solicitada del bus en Hz."),
            ("gpio_set_function(pin, GPIO_FUNC_I2C)", "Enruta SDA y SCL a pines compatibles."),
            ("i2c_write_blocking / i2c_read_blocking", "Transfieren bytes con dirección, STOP o repeated-start."),
            ("i2c_write_timeout_us / i2c_read_timeout_us", "Transfieren con tiempo límite para no esperar indefinidamente."),
            ("i2c_get_hw", "Accede al registro del controlador para configuraciones de bajo nivel."),
        ],
        "pins": "Ejemplo I2C0: GPIO 4 = SDA, GPIO 5 = SCL.",
        "library": "hardware_i2c",
        "wire": "Conecta SDA↔SDA, SCL↔SCL y GND↔GND. Usa pull-ups a 3.3 V; muchos módulos ya los incluyen.",
        "warning": "La dirección de 7 bits depende del dispositivo. Verifica tensión, pull-ups y hoja de datos.",
        "code": r'''#include <cstdint>
#include "pico/stdlib.h"
#include "hardware/i2c.h"

constexpr uint8_t SENSOR_ADDR = 0x68; // Dirección de ejemplo

int main() {
    i2c_init(i2c0, 100'000); // 100 kHz
    gpio_set_function(4, GPIO_FUNC_I2C); // SDA
    gpio_set_function(5, GPIO_FUNC_I2C); // SCL
    gpio_pull_up(4);
    gpio_pull_up(5);

    const uint8_t registro = 0x00;
    uint8_t datos[2] = {};
    const int enviados = i2c_write_blocking(
        i2c0, SENSOR_ADDR, &registro, 1, true
    );
    if (enviados == 1) {
        const int recibidos = i2c_read_blocking(
            i2c0, SENSOR_ADDR, datos, sizeof(datos), false
        );
        if (recibidos == sizeof(datos)) {
            // Procesa datos[0] y datos[1].
        }
    }
}''',
    },
    "SPI": {
        "group": "Buses serie",
        "description": "Bus síncrono rápido con reloj y selección independiente por dispositivo.",
        "theory": "SPI desplaza bits sincronizados por SCK; MOSI y MISO son líneas de datos separadas. No asigna direcciones: cada dispositivo suele tener su propio chip-select, normalmente controlado por GPIO.",
        "resources": ["2 controladores hardware: spi0 y spi1.", "Modo de reloj definido por CPOL y CPHA; el SDK permite palabras de 4 a 16 bits.", "Cada controlador puede compartir SCK/MOSI/MISO entre periféricos con CS independiente."],
        "api": [
            ("spi_init / spi_deinit", "Inicializan o apagan el controlador y fijan la velocidad solicitada."),
            ("spi_set_baudrate", "Cambia la frecuencia solicitada de SCK y devuelve la velocidad configurada."),
            ("spi_set_format", "Configura tamaño de palabra, CPOL, CPHA y orden MSB/LSB."),
            ("gpio_set_function(pin, GPIO_FUNC_SPI)", "Enruta SCK, TX/MOSI y RX/MISO a GPIO compatibles."),
            ("spi_write_blocking / spi_read_blocking", "Transfieren datos en una dirección."),
            ("spi_write_read_blocking", "Transmite y recibe simultáneamente."),
            ("spi_is_readable / spi_is_writable", "Consulta el estado de las FIFOs." ),
        ],
        "pins": "Ejemplo SPI0: GPIO 16 = MISO, GPIO 17 = CS, GPIO 18 = SCK, GPIO 19 = MOSI.",
        "library": "hardware_spi",
        "wire": "Cruza MOSI/MISO según el periférico, comparte GND y controla CS por dispositivo.",
        "warning": "Ajusta frecuencia, modo (CPOL/CPHA), orden de bits y comandos a la hoja de datos.",
        "code": r'''#include <cstdint>
#include "pico/stdlib.h"
#include "hardware/spi.h"

int main() {
    spi_init(spi0, 1'000'000);
    gpio_set_function(16, GPIO_FUNC_SPI); // MISO
    gpio_set_function(18, GPIO_FUNC_SPI); // SCK
    gpio_set_function(19, GPIO_FUNC_SPI); // MOSI

    constexpr uint CS = 17;
    gpio_init(CS);
    gpio_set_dir(CS, GPIO_OUT);
    gpio_put(CS, 1);
    spi_set_format(spi0, 8, SPI_CPOL_0, SPI_CPHA_0, SPI_MSB_FIRST);

    uint8_t tx = 0x9F;
    uint8_t rx = 0;
    gpio_put(CS, 0);
    spi_write_read_blocking(spi0, &tx, &rx, 1);
    gpio_put(CS, 1);
}''',
    },
    "UART": {
        "group": "Buses serie",
        "description": "Puerto serial asíncrono, útil para consolas externas, GPS y módulos.",
        "theory": "UART transmite tramas asíncronas con bit de inicio, datos, paridad opcional y bits de parada. TX y RX deben usar la misma configuración en ambos extremos.",
        "resources": ["2 UART hardware: uart0 y uart1.", "Formato configurable de 5–8 bits de datos, paridad y 1–2 bits de parada.", "El baud rate se solicita en baudios; el generador deriva el divisor del reloj periférico."],
        "api": [
            ("uart_init / uart_deinit", "Inicializan el periférico y configuran velocidad solicitada."),
            ("uart_set_baudrate", "Cambia baudios y devuelve el valor efectivamente configurado."),
            ("uart_set_format", "Configura bits de datos, bits de parada y paridad."),
            ("gpio_set_function(pin, GPIO_FUNC_UART)", "Enruta TX/RX a pines compatibles."),
            ("uart_putc / uart_puts / uart_write_blocking", "Transmiten caracteres o buffers."),
            ("uart_getc / uart_read_blocking", "Reciben caracteres o buffers."),
            ("uart_is_readable / uart_is_writable", "Comprueban si hay datos o espacio en las FIFOs."),
        ],
        "pins": "Ejemplo UART0: GPIO 0 = TX, GPIO 1 = RX.",
        "library": "hardware_uart",
        "wire": "TX de la Pico → RX del otro equipo; RX de la Pico ← TX del otro equipo; GND común.",
        "warning": "Ambos extremos deben usar niveles lógicos compatibles y los mismos baudios.",
        "code": r'''#include "pico/stdlib.h"
#include "hardware/uart.h"

int main() {
    uart_init(uart0, 115200);
    gpio_set_function(0, GPIO_FUNC_UART); // TX
    gpio_set_function(1, GPIO_FUNC_UART); // RX
    uart_set_format(uart0, 8, 1, UART_PARITY_NONE);

    uart_puts(uart0, "Hola por UART\r\n");
    while (true) {
        if (uart_is_readable(uart0)) {
            const char byte = uart_getc(uart0);
            uart_putc(uart0, byte); // Eco
        }
    }
}''',
    },
    "ADC": {
        "group": "Señales analógicas",
        "description": "Convierte tensión de entrada analógica a una cuenta digital.",
        "theory": "El SAR multiplexa señales analógicas a un convertidor de 12 bits. El argumento de adc_select_input() es el índice de canal, no el número GPIO. La conversión a voltios es aproximada y depende de la referencia analógica.",
        "resources": ["5 entradas ADC en RP2350A: ADC0–ADC3 conectadas a GPIO 26–29 y una entrada del sensor de temperatura interno (ADC_TEMPERATURE_CHANNEL_NUM = 4).", "Resolución nativa fija de 12 bits, cuentas 0–4095; el SDK no tiene API para cambiarla.", "Hasta 500 kS/s nominales. En Pico 2 W, GPIO29 se usa para medir VSYS mediante divisor; GPIO26–28 son las entradas analógicas externas de uso general."],
        "api": [
            ("adc_init / adc_deinit", "Inicializan o liberan el ADC."),
            ("adc_gpio_init(gpio)", "Conecta GPIO 26–29 al bloque ADC."),
            ("adc_select_input(channel)", "Selecciona ADC0–ADC4; cambia el canal que lee adc_read()."),
            ("adc_read()", "Realiza una conversión bloqueante de una muestra."),
            ("adc_set_round_robin(mask)", "Activa exploración continua de los canales incluidos en una máscara."),
            ("adc_set_clkdiv(divider)", "Ajusta el divisor de muestreo para el modo FIFO/DMA."),
            ("adc_fifo_setup / adc_fifo_get / adc_fifo_get_blocking / adc_fifo_drain", "Configuran, consumen o limpian la FIFO de muestras."),
            ("adc_set_temp_sensor_enabled(true)", "Habilita el sensor interno; selecciona ADC_TEMPERATURE_CHANNEL_NUM."),
        ],
        "pins": "ADC0/1/2 = GPIO 26/27/28 para entradas externas. ADC3 = GPIO29 está conectado al divisor de VSYS de la Pico 2 W; no lo uses como entrada externa normal.",
        "library": "hardware_adc",
        "wire": "Conecta la señal y GND común. El ejemplo usa ADC0/GPIO 26.",
        "warning": "La entrada debe permanecer entre GND y 3.3 V. La conversión a voltios es aproximada.",
        "code": r'''#include <cstdio>
#include "pico/stdlib.h"
#include "hardware/adc.h"

int main() {
    stdio_init_all();
    adc_init();
    adc_gpio_init(26); // ADC0
    adc_select_input(0);

    while (true) {
        const uint16_t raw = adc_read(); // 0..4095
        const float volts = raw * (3.3f / 4096.0f);
        printf("raw=%u, V~%.3f\n", raw, volts);
        sleep_ms(250);
    }
}''',
    },
    "PWM": {
        "group": "Señales analógicas",
        "description": "Genera una señal periódica de ciclo de trabajo variable; sirve para dimming y control de señales.",
        "theory": "PWM compara un contador repetitivo con un nivel por canal. La frecuencia depende del reloj del sistema, el divisor y TOP (wrap); la resolución depende de TOP.",
        "resources": ["12 slices PWM, cada uno con 2 canales A/B (24 salidas asociables a GPIO).", "Contador de 16 bits con wrap configurable; divisor entero y fraccional 8.4.", "Pines con el mismo slice comparten contador, wrap y divisor, aunque tienen niveles A/B separados."],
        "api": [
            ("gpio_set_function(pin, GPIO_FUNC_PWM)", "Conecta el pin a la salida PWM."),
            ("pwm_gpio_to_slice_num / pwm_gpio_to_channel", "Obtienen slice y canal asociado a un GPIO."),
            ("pwm_get_default_config / pwm_config_set_clkdiv", "Crean configuración base y ajustan divisor de reloj."),
            ("pwm_config_set_wrap / pwm_set_wrap", "Cambian el TOP del contador y, por tanto, la resolución/periodo."),
            ("pwm_init / pwm_set_enabled", "Inicializan y activan/desactivan el slice."),
            ("pwm_set_gpio_level / pwm_set_chan_level", "Cambian el ciclo de trabajo de un canal."),
            ("pwm_set_counter / pwm_get_counter", "Escriben o consultan el contador del slice."),
        ],
        "pins": "Ejemplo: GPIO 15 (conecta a canal PWM correspondiente).",
        "library": "hardware_pwm",
        "wire": "Para LEDs usa resistencia; para motores usa un driver, no el GPIO directamente.",
        "warning": "El contador y divisor determinan frecuencia y resolución. Pines vecinos pueden compartir slice.",
        "code": r'''#include "pico/stdlib.h"
#include "hardware/pwm.h"

constexpr uint PIN = 15;

int main() {
    gpio_set_function(PIN, GPIO_FUNC_PWM);
    const uint slice = pwm_gpio_to_slice_num(PIN);
    pwm_config config = pwm_get_default_config();
    pwm_config_set_wrap(&config, 999);
    pwm_init(slice, &config, true);

    while (true) {
        for (uint16_t level = 0; level <= 999; ++level) {
            pwm_set_gpio_level(PIN, level);
            sleep_ms(2);
        }
        for (int level = 999; level >= 0; --level) {
            pwm_set_gpio_level(PIN, static_cast<uint16_t>(level));
            sleep_ms(2);
        }
    }
}''',
    },
    "Temporizadores": {
        "group": "Tiempo y eventos",
        "description": "Ejecuta tareas periódicas sin bloquear el bucle principal.",
        "theory": "El RP2350 tiene dos temporizadores hardware de 64 bits que cuentan en microsegundos. Cada uno incluye cuatro alarmas que comparan los 32 bits inferiores del contador. Los repeating_timer de pico_time usan estas alarmas para llamar callbacks.",
        "resources": ["2 contadores hardware de 64 bits (timer0 y timer1), en microsegundos.", "4 alarmas por contador: 8 alarmas hardware en total; el compare opera sobre los 32 bits inferiores (máximo ~71.6 min por alarma).", "pico_time ofrece timestamps de 64 bits, absolute_time_t y temporizadores repetitivos."],
        "api": [
            ("time_us_64 / get_absolute_time", "Lee el reloj monotónico de 64 bits."),
            ("delayed_by_ms / delayed_by_us / absolute_time_diff_us", "Construye y calcula diferencias de tiempos absolutos."),
            ("add_repeating_timer_ms / add_repeating_timer_us", "Registra callbacks repetitivos; intervalo negativo programa desde el instante previo."),
            ("cancel_repeating_timer", "Cancela un temporizador repetitivo."),
            ("hardware_alarm_claim / hardware_alarm_unclaim", "Reserva o libera una alarma del timer predeterminado."),
            ("timer_hardware_alarm_claim(timer, alarm)", "Reserva alarma en timer0 o timer1 explícitamente."),
            ("hardware_alarm_set_target / timer_hardware_alarm_set_target", "Programa el instante objetivo en timer predeterminado o en uno explícito."),
            ("hardware_alarm_set_callback / timer_hardware_alarm_set_callback", "Asocia el callback a la alarma y al núcleo actual."),
        ],
        "pins": "No requiere pines dedicados.",
        "library": "pico_stdlib",
        "wire": "Inicializa antes del bucle principal y conserva vivo el objeto repeating_timer_t.",
        "warning": "Mantén breve el callback. Evita printf y operaciones lentas dentro del callback.",
        "code": r'''#include "pico/stdlib.h"

constexpr uint LED_PIN = 15;

bool cada_medio_segundo(repeating_timer_t *timer) {
    (void)timer;
    gpio_xor_mask(1u << LED_PIN);
    return true; // Mantiene el temporizador activo
}

int main() {
    gpio_init(LED_PIN);
    gpio_set_dir(LED_PIN, GPIO_OUT);
    repeating_timer_t timer;
    add_repeating_timer_ms(-500, cada_medio_segundo, nullptr, &timer);

    while (true) {
        tight_loop_contents();
    }
}''',
    },
    "Interrupciones GPIO": {
        "group": "Tiempo y eventos",
        "description": "Reacciona a flancos de botones o señales externas sin consultar el pin continuamente.",
        "theory": "Cada GPIO puede generar eventos de flanco ascendente/descendente o nivel alto/bajo. El SDK proporciona un callback común por núcleo y APIs IRQ por pin; todos los callbacks se ejecutan en contexto de interrupción.",
        "resources": ["4 tipos de evento por GPIO: EDGE_RISE, EDGE_FALL, LEVEL_HIGH y LEVEL_LOW.", "Un evento habilitado se atiende mediante el banco de interrupciones GPIO y callback registrado.", "Las fuentes IRQ globales dependen del núcleo; no bloquees ni hagas I/O lento dentro de una ISR."],
        "api": [
            ("gpio_set_irq_enabled_with_callback", "Instala callback común y habilita eventos para un pin."),
            ("gpio_set_irq_enabled", "Habilita o deshabilita tipos de evento por GPIO."),
            ("gpio_set_dormant_irq_enabled", "Habilita fuentes GPIO para despertar desde dormant."),
            ("gpio_acknowledge_irq", "Confirma eventos pendientes cuando gestionas IRQ de bajo nivel."),
            ("gpio_get_irq_event_mask", "Consulta eventos de interrupción pendientes."),
            ("gpio_set_input_enabled", "Habilita o deshabilita la entrada digital del pin."),
        ],
        "pins": "Ejemplo: botón entre GPIO 14 y GND.",
        "library": "pico_stdlib",
        "wire": "Habilita pull-up y configura el evento de flanco correspondiente.",
        "warning": "El callback se ejecuta en contexto de interrupción: marca un evento y procésalo después.",
        "code": r'''#include "pico/stdlib.h"

constexpr uint BUTTON_PIN = 14;
volatile bool button_event = false;

void gpio_callback(uint gpio, uint32_t events) {
    if (gpio == BUTTON_PIN && (events & GPIO_IRQ_EDGE_FALL)) {
        button_event = true;
    }
}

int main() {
    gpio_init(BUTTON_PIN);
    gpio_set_dir(BUTTON_PIN, GPIO_IN);
    gpio_pull_up(BUTTON_PIN);
    gpio_set_irq_enabled_with_callback(
        BUTTON_PIN, GPIO_IRQ_EDGE_FALL, true, &gpio_callback
    );

    while (true) {
        if (button_event) {
            button_event = false;
            // Procesa el evento fuera de la ISR.
        }
        tight_loop_contents();
    }
}''',
    },
    "DMA": {
        "group": "Transferencia y lógica programable",
        "description": "Transfiere bloques entre memoria y periféricos con poca intervención de CPU.",
        "theory": "El DMA mueve datos entre direcciones de memoria o registros de periféricos. Puede incrementar cada dirección, usar DREQ como ritmo y encadenar canales para transferencias continuas.",
        "resources": ["16 canales DMA en el RP2350.", "Transferencias por elemento de 8, 16 o 32 bits.", "Periféricos como ADC, SPI, UART y PIO pueden sincronizar transferencias mediante DREQ."],
        "api": [
            ("dma_claim_unused_channel / dma_channel_unclaim", "Reserva o libera canales."),
            ("dma_channel_get_default_config", "Obtiene una configuración inicial para el canal."),
            ("channel_config_set_transfer_data_size", "Selecciona DMA_SIZE_8, DMA_SIZE_16 o DMA_SIZE_32."),
            ("channel_config_set_read_increment / channel_config_set_write_increment", "Configura incremento de direcciones."),
            ("channel_config_set_dreq", "Vincula el ritmo de transferencia a una solicitud de periférico."),
            ("dma_channel_configure / dma_start_channel_mask", "Configura y lanza transferencia(s)."),
            ("dma_channel_is_busy / dma_channel_wait_for_finish_blocking", "Consulta o espera finalización."),
        ],
        "pins": "Sin pines dedicados; se usa junto con UART, SPI, ADC, PIO u otros destinos.",
        "library": "hardware_dma",
        "wire": "Configura el tamaño de transferencia, incremento de direcciones y DREQ según el periférico.",
        "warning": "El origen y destino deben seguir válidos hasta que termine la transferencia.",
        "code": r'''#include <cstdint>
#include "pico/stdlib.h"
#include "hardware/dma.h"

int main() {
    uint32_t source[] = {10, 20, 30, 40};
    uint32_t destination[4] = {};
    const int channel = dma_claim_unused_channel(true);

    dma_channel_config config = dma_channel_get_default_config(channel);
    channel_config_set_transfer_data_size(&config, DMA_SIZE_32);
    channel_config_set_read_increment(&config, true);
    channel_config_set_write_increment(&config, true);
    dma_channel_configure(
        channel, &config, destination, source, 4, true
    );
    dma_channel_wait_for_finish_blocking(channel);
    dma_channel_unclaim(channel);
}''',
    },
    "PIO": {
        "group": "Transferencia y lógica programable",
        "description": "Máquinas de estado programables para generar o recibir protocolos digitales deterministas.",
        "theory": "Cada state machine ejecuta instrucciones PIO de ciclo predecible, de manera paralela a la CPU. Programas `.pio` se ensamblan durante la compilación y se cargan en la memoria de instrucciones compartida del bloque.",
        "resources": ["3 bloques PIO × 4 máquinas de estado = 12 state machines.", "Cada bloque tiene 32 palabras de instrucción compartidas por sus cuatro máquinas.", "FIFOs TX/RX de 4 palabras por máquina, unibles para formar FIFO de 8 palabras en una dirección."],
        "api": [
            ("pio_add_program / pio_remove_program", "Carga o elimina programa ensamblado del bloque."),
            ("pio_claim_unused_sm / pio_sm_claim / pio_sm_unclaim", "Reserva o libera una state machine."),
            ("pio_gpio_init / pio_sm_set_consecutive_pindirs", "Enruta pines y establece dirección."),
            ("pio_sm_config / sm_config_set_*", "Configura pines, side-set, divisor de reloj y FIFOs."),
            ("pio_sm_init / pio_sm_set_enabled", "Inicializa, reinicia y activa la máquina."),
            ("pio_sm_put / pio_sm_get / pio_sm_is_tx_fifo_full", "Intercambia datos mediante FIFOs."),
            ("pico_generate_pio_header", "CMake genera el header C/C++ desde un archivo `.pio`."),
        ],
        "pins": "El programa PIO asigna el GPIO; aquí se usa GPIO 15.",
        "library": "hardware_pio",
        "wire": "Guarda el programa `.pio` e incluye el encabezado que genera CMake.",
        "warning": "RP2350 dispone de tres bloques PIO con cuatro máquinas de estado cada uno.",
        "code": r'''; Archivo blink.pio
.program blink
.wrap_target
    set pins, 1 [31]
    set pins, 0 [31]
.wrap''',
        "cmake": '''target_link_libraries(pico_app PRIVATE pico_stdlib hardware_pio)
pico_generate_pio_header(pico_app
    ${CMAKE_CURRENT_LIST_DIR}/blink.pio
)''',
        "extra_code": r'''#include "hardware/pio.h"
#include "blink.pio.h"

void start_pio_blink() {
    constexpr uint PIN = 15;
    PIO pio = pio0;
    const uint offset = pio_add_program(pio, &blink_program);
    const uint sm = pio_claim_unused_sm(pio, true);
    pio_gpio_init(pio, PIN);
    pio_sm_set_consecutive_pindirs(pio, sm, PIN, 1, true);
    pio_sm_config config = blink_program_get_default_config(offset);
    sm_config_set_set_pins(&config, PIN, 1);
    pio_sm_init(pio, sm, offset, &config);
    pio_sm_set_enabled(pio, sm, true);
}''',
    },
    "Watchdog": {
        "group": "Sistema y memoria",
        "description": "Reinicia el microcontrolador si el firmware deja de actualizar el watchdog.",
        "theory": "El watchdog cuenta hacia el vencimiento. El firmware debe actualizarlo solo cuando comprueba que sus tareas críticas siguen sanas; también puede usarse como temporizador de reinicio controlado.",
        "resources": ["1 periférico watchdog compartido por el sistema.", "Puede provocar reinicio, habilitar depuración al vencer y registrar información de reinicio.", "El período máximo y comportamiento exacto dependen del reloj/configuración; consulta la API de watchdog del SDK."],
        "api": [
            ("watchdog_enable(delay_ms, pause_on_debug)", "Activa el watchdog con plazo en milisegundos."),
            ("watchdog_update", "Reinicia el contador de tiempo del watchdog."),
            ("watchdog_disable", "Desactiva el watchdog cuando la configuración lo permite."),
            ("watchdog_caused_reboot", "Comprueba si el último reinicio fue causado por watchdog."),
            ("watchdog_enable_caused_reboot", "Consulta el motivo de reinicio registrado."),
            ("watchdog_reboot", "Solicita un reinicio con demora y datos scratch."),
        ],
        "pins": "No requiere pines.",
        "library": "hardware_watchdog",
        "wire": "Actualiza el watchdog solo después de confirmar que el sistema está sano.",
        "warning": "No lo actualices incondicionalmente desde una interrupción: perdería su propósito.",
        "code": r'''#include "hardware/watchdog.h"

void enable_watchdog() {
    watchdog_enable(5000, true); // 5 segundos
}

void update_after_health_check() {
    // Llama solo si las tareas críticas terminaron correctamente.
    watchdog_update();
}''',
    },
    "RTC": {
        "group": "Sistema y memoria",
        "description": "Reloj calendario del microcontrolador para registrar fecha y hora.",
        "theory": "El RTC mantiene calendario y hora usando el reloj de referencia del sistema. No es un módulo externo con batería: al perder alimentación, no se garantiza conservar la hora.",
        "resources": ["1 reloj calendario hardware con año, mes, día, día de semana, hora, minuto y segundo.", "El SDK intercambia la fecha mediante la estructura datetime_t.", "No se configura una resolución en bits: la API representa segundos y fecha calendario."],
        "api": [
            ("rtc_init / rtc_running", "Inicializa y consulta el estado del RTC."),
            ("rtc_set_datetime / rtc_get_datetime", "Escribe o lee una estructura datetime_t."),
            ("rtc_set_alarm", "Programa alarma de calendario y callback."),
            ("rtc_disable_alarm", "Deshabilita la alarma configurada."),
            ("datetime_to_str", "Formatea fecha/hora para mostrarla."),
        ],
        "pins": "No requiere pines externos.",
        "library": "hardware_rtc",
        "wire": "El ejemplo fija hora de demostración; una app real debe obtener hora válida.",
        "warning": "No sustituye a un RTC con batería para conservar la hora tras quitar alimentación.",
        "code": r'''#include "hardware/rtc.h"

int main() {
    rtc_init();
    datetime_t start{};
    start.year = 2026;
    start.month = 1;
    start.day = 1;
    start.dotw = 4; // 0 = domingo
    start.hour = 12;
    start.min = 0;
    start.sec = 0;
    rtc_set_datetime(&start);

    datetime_t now{};
    while (rtc_get_datetime(&now)) {
        // Usa now.year, now.month, now.day, now.hour, etc.
        break;
    }
}''',
    },
    "Multicore": {
        "group": "Sistema y memoria",
        "description": "Ejecuta una función en el segundo núcleo del RP2350.",
        "theory": "El RP2350 tiene dos núcleos CPU. El SDK permite arrancar core 1 y sincronizar datos; SRAM y periféricos son recursos compartidos y las variables comunes requieren coordinación.",
        "resources": ["2 núcleos seleccionables como Arm Cortex-M33 o Hazard3 RISC-V.", "Core 0 ejecuta el punto de entrada normal; core 1 puede arrancarse desde el SDK.", "Colas multicore, mutexes, semáforos y primitivas de sincronización ayudan a transferir trabajo."],
        "api": [
            ("multicore_launch_core1", "Lanza una función en core 1."),
            ("multicore_reset_core1", "Reinicia core 1."),
            ("multicore_fifo_push_blocking / multicore_fifo_pop_blocking", "Intercambia palabras entre núcleos mediante FIFO."),
            ("multicore_fifo_rvalid / multicore_fifo_wready", "Consulta disponibilidad de lectura y escritura."),
            ("multicore_lockout_start_blocking / multicore_lockout_end_blocking", "Pausa cooperativamente el otro núcleo para operaciones sensibles."),
            ("mutex_init / mutex_enter_blocking / mutex_exit", "Protege secciones críticas compartidas."),
        ],
        "pins": "No requiere pines.",
        "library": "pico_multicore",
        "wire": "Usa colas, mutexes o primitivas de sincronización del SDK para compartir estado.",
        "warning": "Evita compartir variables sin sincronización entre núcleos.",
        "code": r'''#include "pico/multicore.h"
#include "pico/stdlib.h"

void core1_entry() {
    while (true) {
        // Trabajo independiente del núcleo 1.
        tight_loop_contents();
    }
}

int main() {
    multicore_launch_core1(core1_entry);
    while (true) {
        // Trabajo del núcleo 0.
        tight_loop_contents();
    }
}''',
    },
    "Flash": {
        "group": "Sistema y memoria",
        "description": "Almacena configuración persistente en la memoria Flash externa de la placa.",
        "theory": "El RP2350 ejecuta código desde Flash externa XIP. Se borra por sectores y se programa por páginas; durante la operación se interrumpe XIP. pico_flash proporciona flash_safe_execute para coordinar interrupciones y el otro núcleo cuando se usa pico_multicore.",
        "resources": ["La placa Pico 2 W incorpora 4 MB de Flash externa; capacidad distinta en otros diseños RP2350.", "Tamaño de sector usual: 4 KB; tamaño de página de programación: 256 bytes.", "La API recibe offsets relativos al comienzo del dispositivo Flash."],
        "api": [
            ("flash_get_unique_id", "Lee el identificador único del chip Flash."),
            ("flash_range_erase(offset, count)", "Borra sectores alineados; el tamaño debe ser múltiplo de sector."),
            ("flash_range_program(offset, data, count)", "Programa páginas alineadas; count debe cumplir alineación/tamaño."),
            ("flash_safe_execute", "Ejecuta una operación de Flash en una ventana segura y devuelve un código de estado."),
            ("flash_safe_execute_core_init", "Debe inicializarse desde core 1 si se usa pico_multicore y se requiere coordinación segura."),
        ],
        "pins": "Sin pines de usuario; la Flash está conectada internamente.",
        "library": "hardware_flash + pico_flash",
        "wire": "Reserva sectores al final de la Flash y define cuidadosamente el mapa de memoria.",
        "warning": "El borrado ocurre por sectores y la programación por páginas. Reserva la región en el mapa de memoria; el buffer de datos debe estar en SRAM. En sistemas multicore llama flash_safe_execute_core_init() desde core 1.",
        "code": r'''#include <stdint.h>
#include "hardware/flash.h"
#include "pico/flash.h"

struct FlashWrite {
    uint32_t offset;       // Sector reservado y alineado
    const uint8_t *page;   // Buffer en SRAM, alineado a FLASH_PAGE_SIZE
};

void erase_and_program(void *context) {
    const auto *write = static_cast<const FlashWrite *>(context);
    flash_range_erase(write->offset, FLASH_SECTOR_SIZE);
    flash_range_program(write->offset, write->page, FLASH_PAGE_SIZE);
}

int write_reserved_flash(uint32_t offset, const uint8_t *page_in_sram) {
    FlashWrite write{offset, page_in_sram};
    return flash_safe_execute(erase_and_program, &write, 1000);
    // Comprueba PICO_OK; en timeout la operación puede haberse ejecutado.
}

// En core 1, antes de iniciar trabajo que pueda usar Flash:
// flash_safe_execute_core_init();''',
    },
    "USB": {
        "group": "Conectividad",
        "description": "La forma más sencilla de depurar es enviar stdio por USB CDC.",
        "theory": "El RP2350 integra un controlador USB 1.1 de velocidad completa. El SDK ofrece CDC stdio para consola y TinyUSB para implementar clases USB como HID o CDC.",
        "resources": ["1 controlador USB 1.1 full-speed (12 Mbit/s de señalización).", "USB CDC para stdio es la ruta de depuración más sencilla.", "TinyUSB permite construir dispositivos USB; la clase/endpoint depende de la aplicación."],
        "api": [
            ("pico_enable_stdio_usb(target, 1)", "Activa CDC stdio desde CMake."),
            ("stdio_init_all / stdio_usb_init", "Inicializa stdio o el backend USB correspondiente."),
            ("printf / puts / getchar", "Usa la API estándar C para transmitir/recibir texto."),
            ("tud_task / tud_cdc_write / tud_cdc_read", "APIs TinyUSB para aplicación USB personalizada."),
        ],
        "pins": "Se conecta mediante el puerto USB integrado.",
        "library": "pico_stdlib",
        "wire": "Habilita salida USB en CMake y abre el puerto serial enumerado por el sistema.",
        "warning": "El monitor puede tardar en enumerar; da tiempo al host antes de esperar datos.",
        "code": r'''#include <cstdio>
#include "pico/stdlib.h"

int main() {
    stdio_init_all();
    sleep_ms(1500);
    printf("Hola desde la Pico 2 W\n");
    while (true) {
        tight_loop_contents();
    }
}''',
        "cmake": '''pico_enable_stdio_usb(pico_app 1)
pico_enable_stdio_uart(pico_app 0)''',
    },
    "Interpolador y HSTX": {
        "group": "Sistema y memoria",
        "description": "Interpolador para cálculos enteros eficientes y HSTX para transmisión digital de alta velocidad.",
        "theory": "El interpolador acelera operaciones de extracción de bits, lookup y mezcla entera; HSTX serializa flujos digitales de alta velocidad. Son periféricos de bajo nivel: la aplicación define el cálculo o protocolo.",
        "resources": ["2 interpoladores por núcleo CPU (4 en total); cada interpolador dispone de 2 lanes.", "1 bloque HSTX con salidas digitales dedicadas en el RP2350.", "La biblioteca hardware_* ofrece acceso a registros y configuración específica; no es un protocolo de pantalla listo para usar."],
        "api": [
            ("interp_claim_lane / interp_claim_lane_mask", "Reserva lanes para uso exclusivo."),
            ("interp_config_set_signed / interp_config_set_mask / interp_config_set_shift", "Configura extracción, máscara y desplazamiento."),
            ("interp_set_config / interp_put / interp_get", "Instala configuración y opera con los acumuladores."),
            ("hstx_ctrl_hw / hstx_fifo_hw", "Acceso de bajo nivel al control y FIFO HSTX."),
            ("hardware/interp.h y hardware/hstx.h", "Cabeceras del SDK; consulta los ejemplos específicos para secuencia y tiempos."),
        ],
        "pins": "Funciones avanzadas: verifica la asignación de pines y ejemplo oficial aplicable.",
        "library": "hardware_interp / hardware_hstx",
        "wire": "Úsalos solo tras consultar el datasheet y los ejemplos del SDK para el protocolo elegido.",
        "warning": "No son sustitutos generales de GPIO, SPI o PWM; requieren configuración de bajo nivel.",
        "code": r'''#include "hardware/interp.h"
#include "hardware/hstx.h"

// La configuración exacta depende del algoritmo (interp)
// o del protocolo y el hardware conectado (HSTX).
// Consulta los ejemplos oficiales del Pico SDK antes de iniciar el periférico.''',
    },
}

PERIPHERAL_CONFIGURATION_EXAMPLES = {
    "GPIO digital": r'''// Selecciona entrada/salida, pulls y función alternativa.
gpio_set_dir(15, GPIO_OUT);
gpio_set_drive_strength(15, GPIO_DRIVE_STRENGTH_4MA);
gpio_pull_up(14);
gpio_set_function(4, GPIO_FUNC_I2C);''',
    "I2C": r'''// Cambia velocidad y timeout de una transferencia.
uint actual_hz = i2c_set_baudrate(i2c0, 400'000);
int count = i2c_read_timeout_us(
    i2c0, 0x68, buffer, sizeof(buffer), false, 10'000
);''',
    "SPI": r'''// Cambia reloj, tamaño de palabra y modo SPI.
uint actual_hz = spi_set_baudrate(spi0, 4'000'000);
spi_set_format(spi0, 8, SPI_CPOL_1, SPI_CPHA_1, SPI_MSB_FIRST);''',
    "UART": r'''// Cambia baud rate y formato de trama (8N1).
uint actual_baud = uart_set_baudrate(uart0, 9600);
uart_set_format(uart0, 8, 1, UART_PARITY_NONE);''',
    "ADC": r'''// Selección manual de canal ADC2 (GPIO 28).
adc_select_input(2);
uint16_t sample = adc_read();

// Sensor interno de temperatura (canal especial, no es GPIO).
adc_set_temp_sensor_enabled(true);
adc_select_input(ADC_TEMPERATURE_CHANNEL_NUM);
uint16_t temperature_sample = adc_read();

// Para adquisición continua: ADC0, ADC1 y ADC2 en round-robin.
adc_set_round_robin((1u << 0) | (1u << 1) | (1u << 2));
adc_fifo_setup(true, true, 1, false, false);
adc_set_clkdiv(0); // Muestreo a la máxima tasa del ADC.''',
    "PWM": r'''// Cambia periodo, divisor de reloj y duty.
pwm_set_wrap(slice, 999);       // TOP; cuenta 0..999
pwm_set_clkdiv(slice, 4.0f);   // Menor frecuencia al aumentar divisor
pwm_set_gpio_level(PIN, 250);  // 25% del periodo (aprox.)''',
    "Temporizadores": r'''// Cambia el intervalo periódico a 1 segundo.
add_repeating_timer_ms(-1000, callback, nullptr, &timer);

// Consulta el contador monotónico del sistema en microsegundos.
uint64_t timestamp_us = time_us_64();''',
    "Interrupciones GPIO": r'''// Cambia evento habilitado y flanco detectado.
gpio_set_irq_enabled(
    BUTTON_PIN, GPIO_IRQ_EDGE_RISE | GPIO_IRQ_EDGE_FALL, true
);''',
    "DMA": r'''// Cambia ancho, incremento y ritmo por periférico (DREQ).
channel_config_set_transfer_data_size(&config, DMA_SIZE_16);
channel_config_set_read_increment(&config, true);
channel_config_set_write_increment(&config, false);
channel_config_set_dreq(&config, DREQ_SPI0_RX);''',
    "PIO": r'''// El divisor cambia velocidad de ejecución de la state machine.
sm_config_set_clkdiv(&config, 10.0f);
sm_config_set_fifo_join(&config, PIO_FIFO_JOIN_TX);
pio_sm_init(pio, sm, offset, &config);''',
    "Watchdog": r'''// Cambia el plazo; watchdog_update() reinicia el conteo.
watchdog_enable(10'000, true); // 10 segundos
watchdog_update();''',
    "RTC": r'''// Modifica los campos de fecha/hora y los carga al reloj.
datetime_t now{};
if (rtc_get_datetime(&now)) {
    now.hour = 13;
    now.min = 30;
    rtc_set_datetime(&now);
}''',
    "Multicore": r'''// Core 0 arranca core 1 y envía una palabra por la FIFO.
multicore_launch_core1(core1_entry);
multicore_fifo_push_blocking(42);
// En core1_entry(): const uint32_t received = multicore_fifo_pop_blocking();''',
    "Flash": r'''// Usa una región reservada, offsets alineados y un buffer en SRAM.
// Encapsula erase + program en un callback y pásalo a flash_safe_execute().
int status = write_reserved_flash(offset, page_in_sram);
if (status != PICO_OK) {
    // Trata el error: en timeout la operación puede haberse ejecutado.
}''',
    "USB": r'''// Selecciona el backend de stdio durante la configuración CMake.
pico_enable_stdio_usb(pico_app 1)
pico_enable_stdio_uart(pico_app 0)
// Después de stdio_init_all():
printf("Consola USB lista\\n");''',
    "Interpolador y HSTX": r'''// Interpolador: ajustar máscara/desplazamiento según algoritmo.
interp_config config = interp_default_config();
interp_config_set_mask(&config, 0, 15);
interp_config_set_shift(&config, 0);
interp_set_config(interp0, 0, &config);

// HSTX: configuración de bajo nivel; consulta el ejemplo
// HSTX/DVI oficial para pines, clocking y FIFO.''',
}

SDK_API = [
    ("gpio_init", "Prepara un GPIO para uso digital.", "gpio_init(LED_PIN);"),
    ("gpio_set_dir", "Configura el pin como entrada o salida.", "gpio_set_dir(LED_PIN, GPIO_OUT);"),
    ("gpio_put / gpio_get", "Escribe o lee el nivel lógico.", "gpio_put(LED_PIN, true);\nbool level = gpio_get(BUTTON_PIN);"),
    ("gpio_pull_up / gpio_pull_down", "Activa las resistencias pull internas.", "gpio_pull_up(BUTTON_PIN);"),
    ("gpio_set_function", "Conecta un GPIO a la función alternativa.", "gpio_set_function(4, GPIO_FUNC_I2C);"),
    ("sleep_ms / sleep_us", "Espera bloqueante en milisegundos o microsegundos.", "sleep_ms(100);\nsleep_us(20);"),
    ("stdio_init_all", "Inicializa las salidas stdio habilitadas.", "stdio_init_all();\nprintf(\"ready\\n\");"),
    ("i2c_init / i2c_write_blocking / i2c_read_blocking", "Configura I2C y transfiere bytes.", "i2c_init(i2c0, 100'000);"),
    ("spi_init / spi_write_read_blocking", "Configura SPI y realiza una transferencia.", "spi_init(spi0, 1'000'000);"),
    ("uart_init / uart_puts / uart_getc", "Inicializa UART y transmite/recibe.", "uart_init(uart0, 115200);"),
    ("adc_init / adc_select_input / adc_read", "Selecciona y lee una entrada ADC.", "adc_init();\nadc_select_input(0);\nuint16_t raw = adc_read();"),
    ("pwm_gpio_to_slice_num / pwm_set_gpio_level", "Configura salida PWM y ciclo de trabajo.", "uint slice = pwm_gpio_to_slice_num(PIN);"),
    ("add_repeating_timer_ms", "Registra un callback con periodo en milisegundos.", "add_repeating_timer_ms(-100, callback, nullptr, &timer);"),
    ("gpio_set_irq_enabled_with_callback", "Habilita un evento de interrupción GPIO.", "gpio_set_irq_enabled_with_callback(PIN, GPIO_IRQ_EDGE_FALL, true, callback);"),
    ("dma_channel_configure", "Configura y lanza un canal DMA.", "dma_channel_configure(channel, &config, dst, src, count, true);"),
    ("pio_add_program / pio_sm_init", "Carga programa PIO y configura una state machine.", "uint offset = pio_add_program(pio0, &program);"),
    ("watchdog_enable / watchdog_update", "Activa y alimenta el watchdog.", "watchdog_enable(5000, true);\nwatchdog_update();"),
    ("multicore_launch_core1", "Inicia la función de usuario en el núcleo 1.", "multicore_launch_core1(core1_entry);"),
    ("cyw43_arch_init / cyw43_arch_deinit", "Inicializa o libera el driver inalámbrico CYW43.", "if (cyw43_arch_init() != 0) return 1;"),
    ("flash_range_erase / flash_range_program", "Borra sectores y programa páginas de Flash.", "flash_range_erase(offset, FLASH_SECTOR_SIZE);"),
]


def page_heading(eyebrow: str, title: str, subtitle: str) -> None:
    st.html(
        f"""
        <section class="pico-hero">
            <div class="eyebrow">{escape(eyebrow)}</div>
            <h1>{escape(title)}</h1>
            <p>{escape(subtitle)}</p>
        </section>
        """
    )


def show_code(body: str, language: str | None = None) -> None:
    st.code(body, language=language, wrap_lines=True)


def render_home() -> None:
    page_heading(
        "Guía interactiva · Pico SDK · C/C++",
        "Construye con la Pico 2 W",
        "Una guía práctica para entender el RP2350, conectar periféricos y escribir firmware con ejemplos del SDK oficial.",
    )

    metric_columns = st.columns(4)
    for column, value, label in zip(
        metric_columns,
        ("RP2350", "2", "520 KB", "2.4 GHz"),
        ("microcontrolador", "núcleos seleccionables", "SRAM integrada", "Wi-Fi de la variante W"),
    ):
        column.metric(label, value)

    st.subheader("Empieza por aquí", icon=":material/route:")
    left, right = st.columns(2)
    with left, st.container(border=True):
        st.markdown("#### 01 · Prepara el entorno")
        st.write("Instala Pico SDK, CMake, Ninja y el toolchain; configura `PICO_SDK_PATH`.")
        show_code(
            "cmake -S . -B build -DPICO_BOARD=pico2_w -G Ninja\n"
            "cmake --build build",
            language="powershell",
        )
    with right, st.container(border=True):
        st.markdown("#### 02 · Prueba un GPIO")
        st.write("Compila un programa pequeño, carga el UF2 y valida el cableado con una resistencia.")
        show_code(
            '#include "pico/stdlib.h"\n'
            "int main() {\n"
            "    gpio_init(15);\n"
            "    gpio_set_dir(15, GPIO_OUT);\n"
            "    while (true) { gpio_xor_mask(1u << 15); sleep_ms(500); }\n"
            "}",
            language="cpp",
        )

    st.subheader("Explora la guía", icon=":material/explore:")
    cards = [
        ("Arquitectura", "RP2350, núcleos, memoria y el chip CYW43439."),
        ("Periféricos", "GPIO, I2C, SPI, UART, PWM, ADC, DMA, PIO y más."),
        ("API del Pico SDK", "Funciones principales y patrones de uso."),
        ("Wi-Fi y Bluetooth", "Conecta redes 2.4 GHz y explora BLE."),
        ("DSP y TinyML", "CMSIS-DSP, clasificación SVM y operadores CMSIS-NN."),
        ("Compilar y cargar", "Flujo CMake/Ninja, UF2 y depuración serial."),
    ]
    card_columns = st.columns(3)
    for index, (title, body) in enumerate(cards):
        with card_columns[index % 3], st.container(border=True):
            st.markdown(f"**{title}**")
            st.caption(body)

    st.info(
        "Todos los GPIO son de 3.3 V. Confirma siempre el pinout, límites eléctricos "
        "y protocolo del módulo antes de conectar hardware.",
        icon=":material/electrical_services:",
    )


def render_architecture() -> None:
    page_heading(
        "01 · Plataforma",
        "Arquitectura de la Pico 2 W",
        "La placa une el RP2350, memoria, conectividad inalámbrica y los bloques de E/S programables.",
    )
    st.subheader("Mapa del sistema", icon=":material/schema:")
    show_code(
        """Aplicación C/C++
       │
       ├── Pico SDK: stdlib, hardware_*, CYW43, lwIP
       │
       ├── RP2350
       │   ├── 2 núcleos: Arm Cortex-M33 o Hazard3 RISC-V
       │   ├── 520 KB SRAM, DMA, GPIO, ADC, PWM, UART, SPI, I2C
       │   └── 3 bloques PIO × 4 máquinas de estado
       │
       ├── Flash externa de la placa: 4 MB
       └── CYW43439: Wi-Fi 2.4 GHz + Bluetooth LE""",
        language="text",
    )
    st.warning(
        "La opción Arm/RISC-V selecciona la arquitectura de los dos núcleos al compilar "
        "el firmware; no son cuatro núcleos activos a la vez.",
        icon=":material/info:",
    )

    col_a, col_b = st.columns(2)
    with col_a, st.container(border=True):
        st.markdown("#### Arm Cortex-M33")
        st.write(
            "Arquitectura Armv8-M con TrustZone-M y extensiones DSP. "
            "CMSIS-DSP y CMSIS-NN pueden usar implementaciones para Cortex-M33; "
            "este núcleo no tiene Helium/MVE."
        )
    with col_b, st.container(border=True):
        st.markdown("#### Hazard3 RISC-V")
        st.write(
            "Núcleo RV32 de la familia Hazard3. Puede seleccionarse como objetivo "
            "en toolchains y configuraciones del SDK compatibles; comprueba el soporte "
            "de cada biblioteca externa para este objetivo."
        )

    st.subheader("Recursos principales")
    st.dataframe(
        [
            {"Recurso": "CPU", "Descripción": "2 núcleos, hasta 150 MHz; Arm Cortex-M33 o Hazard3 RISC-V"},
            {"Recurso": "SRAM", "Descripción": "520 KB integrados en el RP2350"},
            {"Recurso": "Flash", "Descripción": "4 MB externos en la placa Pico 2 W"},
            {"Recurso": "PIO", "Descripción": "3 bloques PIO, 4 state machines por bloque"},
            {"Recurso": "Radio", "Descripción": "CYW43439: Wi-Fi 2.4 GHz y Bluetooth LE"},
            {"Recurso": "ADC", "Descripción": "12 bits; cuatro entradas externas en GPIO 26–29"},
        ],
        hide_index=True,
        width="stretch",
    )
    st.caption(
        "Consulta el datasheet de la revisión de placa y el pinout oficial: "
        "ciertas señales se reservan para funciones internas."
    )


def render_peripherals() -> None:
    page_heading(
        "02 · Entrada/salida",
        "Periféricos con ejemplos",
        "Explora los recursos del RP2350, entiende la teoría y aprende qué APIs del SDK configuran cada periférico.",
    )
    peripheral_name = st.selectbox(
        "Selecciona un periférico",
        options=list(PERIPHERALS),
        key="peripheral_selector",
    )
    item = PERIPHERALS[peripheral_name]
    st.badge(item["group"], icon=":material/category:")
    st.markdown(f"### {peripheral_name}")
    st.write(item["description"])

    meta_cols = st.columns(2)
    meta_cols[0].markdown(f"**Pines**  \n{item['pins']}")
    meta_cols[1].markdown(f"**Biblioteca de CMake**  \n`{item['library']}`")

    theory_tab, api_tab, example_tab = st.tabs(
        ["Teoría y recursos", "API del SDK", "Ejemplo C/C++"]
    )
    with theory_tab:
        st.markdown("#### Cómo funciona")
        st.write(item["theory"])
        st.markdown("#### Recursos y capacidades")
        for resource in item["resources"]:
            st.markdown(f"- {resource}")
        with st.container(border=True):
            st.markdown("**Cableado o configuración inicial**")
            st.write(item["wire"])
        st.warning(item["warning"], icon=":material/warning:")
    with api_tab:
        st.markdown("#### Funciones principales")
        st.dataframe(
            [
                {"API del Pico SDK": function, "Uso": description}
                for function, description in item["api"]
            ],
            hide_index=True,
            width="stretch",
        )
        st.markdown("#### Cambiar parámetros")
        st.caption(
            "Estas llamadas muestran qué función modificar al cambiar velocidad, "
            "canal, resolución efectiva, formato o comportamiento."
        )
        show_code(
            PERIPHERAL_CONFIGURATION_EXAMPLES[peripheral_name],
            language="cpp",
        )
        if peripheral_name == "ADC":
            st.info(
                "La resolución ADC del hardware es fija en 12 bits: no existe una API "
                "para pasarla a 8 o 16 bits. Cambia el canal con `adc_select_input()`; "
                "el muestreo continuo se configura con round-robin, FIFO y divisor.",
                icon=":material/info:",
            )
    with example_tab:
        st.markdown("#### Ejemplo")
        st.write(item["description"])
        show_code(
            item["code"],
            language="text" if peripheral_name == "PIO" else "cpp",
        )
        if item.get("extra_code"):
            st.caption("Código C/C++ que inicializa la máquina de estados:")
            show_code(item["extra_code"], language="cpp")
        cmake = item.get("cmake")
        if cmake:
            st.markdown("#### Configuración CMake requerida")
            show_code(cmake, language="cmake")

    st.caption(
        "Los pines alternativos dependen de la función del pin. Comprueba el pinout "
        "y el datasheet del módulo antes de cablear. "
        "[Datasheet RP2350](https://datasheets.raspberrypi.com/rp2350/rp2350-datasheet.pdf) · "
        "[Referencia Pico SDK](https://www.raspberrypi.com/documentation/microcontrollers/c_sdk.html)"
    )


def render_sdk_api() -> None:
    page_heading(
        "03 · Referencia",
        "API esencial del Pico SDK",
        "Busca una función, revisa su propósito y abre un ejemplo mínimo. La documentación oficial del SDK contiene todas las firmas y variantes.",
    )
    query = st.text_input(
        "Filtrar funciones",
        placeholder="Ejemplo: gpio, adc, interrupción, multicore",
        key="api_filter",
    )
    filtered = [
        row
        for row in SDK_API
        if not query
        or query.casefold() in row[0].casefold()
        or query.casefold() in row[1].casefold()
    ]
    st.caption(f"{len(filtered)} funciones coinciden")
    for function, description, example in filtered:
        with st.expander(f"`{function}` · {description}"):
            show_code(example, language="cpp")

    st.subheader("Patrón habitual de un firmware")
    show_code(
        r'''#include <cstdio>
#include "pico/stdlib.h"

int main() {
    stdio_init_all();
    // Inicializa aquí los periféricos.

    while (true) {
        // Lee entradas, procesa y actualiza salidas.
        tight_loop_contents();
    }
}''',
        language="cpp",
    )


def render_wireless() -> None:
    page_heading(
        "04 · Conectividad",
        "Wi-Fi y Bluetooth LE",
        "En la variante W, el CYW43439 aporta radio de 2.4 GHz. El Pico SDK integra el driver CYW43 y opciones de pila lwIP.",
    )
    st.subheader("Conectar a Wi-Fi como estación")
    st.write(
        "Añade `pico_cyw43_arch_lwip_threadsafe_background` a las bibliotecas "
        "del ejecutable. Usa credenciales de prueba; no guardes secretos reales en el repositorio."
    )
    show_code(
        '''target_link_libraries(pico_app
    pico_stdlib
    pico_cyw43_arch_lwip_threadsafe_background
)''',
        language="cmake",
    )
    show_code(
        r'''#include <cstdio>
#include "pico/cyw43_arch.h"
#include "pico/stdlib.h"

constexpr char WIFI_SSID[] = "TU_RED_2_4_GHZ";
constexpr char WIFI_PASSWORD[] = "TU_CLAVE";

int main() {
    stdio_init_all();
    if (cyw43_arch_init() != 0) {
        printf("Fallo al inicializar CYW43\n");
        return 1;
    }

    cyw43_arch_enable_sta_mode();
    const int result = cyw43_arch_wifi_connect_timeout_ms(
        WIFI_SSID,
        WIFI_PASSWORD,
        CYW43_AUTH_WPA2_AES_PSK,
        30'000
    );
    if (result != 0) {
        printf("No se pudo conectar: %d\n", result);
        cyw43_arch_deinit();
        return 1;
    }

    while (true) {
        cyw43_arch_gpio_put(CYW43_WL_GPIO_LED_PIN, 1);
        sleep_ms(500);
        cyw43_arch_gpio_put(CYW43_WL_GPIO_LED_PIN, 0);
        sleep_ms(500);
    }
}''',
        language="cpp",
    )
    st.info(
        "El ejemplo presupone autenticación WPA2-PSK y red de 2.4 GHz. "
        "Para otros modos, elige el código de autenticación adecuado. "
        "Al usar la variante `threadsafe_background`, no hace falta llamar "
        "`cyw43_arch_poll()` desde el bucle principal.",
        icon=":material/lightbulb:",
    )

    with st.expander("Bluetooth LE"):
        st.write(
            "El soporte BLE se implementa con BTstack y el driver CYW43. "
            "El flujo típico define si la Pico actúa como periférico o central, "
            "registra servicios/características GATT y procesa callbacks. "
            "Usa un ejemplo BLE oficial de la misma versión del Pico SDK: "
            "el target CMake y el transporte dependen del rol y del ejemplo."
        )
        show_code(
            '''#include "pico/cyw43_arch.h"
#include "btstack.h"

// Inicialización y callbacks BLE: seguir el ejemplo oficial elegido.
// No es suficiente inicializar Wi-Fi para habilitar BLE.''',
            language="cpp",
        )


def render_dsp_ml() -> None:
    page_heading(
        "05 · Señal e inferencia",
        "DSP, SVM y redes neuronales",
        "CMSIS-DSP acelera operaciones de señal y ofrece SVM binario; CMSIS-NN aporta operadores de redes cuantizadas para Cortex-M.",
    )
    st.info(
        "El RP2350 usa un Cortex-M33 con DSP, no Helium/MVE. CMSIS-DSP y CMSIS-NN "
        "son dependencias externas al Pico SDK: comprueba licencias, versiones y "
        "uso de SRAM/Flash antes de integrarlas.",
        icon=":material/info:",
    )

    dsp_tab, svm_tab, nn_tab = st.tabs(
        ["CMSIS-DSP", "SVM", "CMSIS-NN / TinyML"],
        default="CMSIS-DSP",
    )
    with dsp_tab:
        st.markdown("#### Integrar la biblioteca")
        show_code(
            '''set(CMSISCORE "${CMAKE_CURRENT_LIST_DIR}/external/CMSIS_6/CMSIS/Core"
    CACHE PATH "Ruta que contiene Include/")
add_subdirectory(external/CMSIS-DSP/Source)
target_compile_definitions(CMSISDSP PUBLIC ARM_MATH_DSP)
target_link_libraries(pico_app PRIVATE pico_stdlib CMSISDSP)''',
            language="cmake",
        )
        st.markdown("#### FIR pasa-bajos de cinco coeficientes")
        st.write(
            "Este promedio móvil procesa bloques de ocho muestras. El estado se conserva "
            "entre llamadas para que los bloques sean continuos."
        )
        show_code(
            r'''#include "arm_math.h"

constexpr uint32_t TAPS = 5;
constexpr uint32_t BLOCK = 8;
const float32_t coeffs[TAPS] = {0.2f, 0.2f, 0.2f, 0.2f, 0.2f};
float32_t state[TAPS + BLOCK - 1] = {};
arm_fir_instance_f32 fir{};

void init_filter() {
    arm_fir_init_f32(&fir, TAPS, coeffs, state, BLOCK);
}

void filter_block(const float32_t *input, float32_t *output) {
    arm_fir_f32(&fir, input, output, BLOCK);
}''',
            language="cpp",
        )
        st.caption(
            "Otras APIs: `arm_dot_prod_f32`, `arm_rfft_fast_f32`, "
            "`arm_biquad_cascade_df1_f32`, `arm_mean_f32`."
        )

    with svm_tab:
        st.markdown("#### Clasificador SVM lineal binario")
        st.write(
            "CMSIS-DSP ejecuta, pero no entrena, el clasificador. Exporta desde tu "
            "entrenamiento las etiquetas, los vectores de soporte, los coeficientes "
            "duales, el intercepto y el mismo preprocesamiento de características."
        )
        show_code(
            r'''#include "arm_math.h"

constexpr uint32_t SUPPORT_COUNT = 1;
constexpr uint32_t FEATURES = 2;
const float32_t support_vectors[SUPPORT_COUNT * FEATURES] = {1.0f, 0.0f};
const float32_t dual_coefficients[SUPPORT_COUNT] = {1.0f};
const int32_t classes[2] = {0, 1};
arm_svm_linear_instance_f32 model{};

void init_model() {
    arm_svm_linear_init_f32(
        &model, SUPPORT_COUNT, FEATURES, 0.0f,
        dual_coefficients, support_vectors, classes
    );
}

int32_t predict(const float32_t features[FEATURES]) {
    int32_t label = 0;
    arm_svm_linear_predict_f32(&model, features, &label);
    return label;
}''',
            language="cpp",
        )
        st.warning(
            "Los parámetros numéricos son ilustrativos, no un modelo entrenado. "
            "La API predice una de dos clases; características y normalización "
            "deben coincidir exactamente con el entrenamiento.",
            icon=":material/warning:",
        )

    with nn_tab:
        st.markdown("#### Integrar CMSIS-NN")
        st.write(
            "CMSIS-NN no carga modelos por sí solo. Añade sus operadores directamente "
            "o usa TensorFlow Lite for Microcontrollers (TFLM) con kernels compatibles."
        )
        show_code(
            '''add_subdirectory(external/CMSIS-NN)
target_link_libraries(pico_app PRIVATE pico_stdlib cmsis-nn)''',
            language="cmake",
        )
        st.markdown("#### Operador fully connected int8")
        st.write(
            "Esqueleto conceptual de una capa. En un modelo real, usa sin alterarlos "
            "los pesos, biases, offsets y parámetros de cuantización exportados."
        )
        show_code(
            r'''#include <cstdint>
#include "arm_nnfunctions.h"

const int8_t input_data[2] = {20, -10};
const int8_t weights[4] = {1, 0, 0, 1};
const int32_t bias[2] = {0, 0};
int8_t output_data[2] = {};

bool run_layer() {
    const cmsis_nn_context ctx{nullptr, 0};
    const cmsis_nn_fc_params fc{
        0, 0, 0, {-128, 127}
    };
    const cmsis_nn_per_tensor_quant_params quant{
        1073741824, 1 // Solo valores ilustrativos
    };
    const cmsis_nn_dims input_dims{1, 1, 1, 2};
    const cmsis_nn_dims filter_dims{2, 1, 1, 2};
    const cmsis_nn_dims bias_dims{1, 1, 1, 2};
    const cmsis_nn_dims output_dims{1, 1, 1, 2};

    return arm_fully_connected_s8(
        &ctx, &fc, &quant, &input_dims, input_data,
        &filter_dims, weights, &bias_dims, bias,
        &output_dims, output_data
    ) == ARM_CMSIS_NN_SUCCESS;
}''',
            language="cpp",
        )
        st.caption(
            "Verifica tamaños de scratch buffer para la arquitectura objetivo y "
            "compara los resultados contra una implementación de referencia."
        )


def render_build() -> None:
    page_heading(
        "06 · Flujo de trabajo",
        "Compilar, cargar y depurar",
        "Un flujo repetible con CMake y Ninja desde el proyecto de ejemplo incluido en este repositorio.",
    )
    st.subheader("Requisitos")
    st.markdown(
        """
        - Raspberry Pi Pico SDK y un toolchain Arm/RISC-V compatible con el objetivo elegido.
        - CMake, Ninja y Git.
        - En VS Code: extensión Raspberry Pi Pico y su asistente de instalación.
        - `PICO_SDK_PATH` configurado si CMake no lo descubre automáticamente.
        """
    )
    st.subheader("Configurar y compilar")
    show_code(
        "cmake -S adc_test1 -B adc_test1/build -DPICO_BOARD=pico2_w -G Ninja\n"
        "cmake --build adc_test1/build",
        language="powershell",
    )
    st.markdown("#### Cargar UF2")
    st.markdown(
        """
        1. Mantén **BOOTSEL** pulsado mientras conectas la placa por USB.
        2. Suelta BOOTSEL cuando aparezca la unidad de almacenamiento.
        3. Copia `adc_test1/build/adc_test1.uf2` a esa unidad.
        4. La placa se reinicia y ejecuta el firmware.
        """
    )
    st.markdown("#### Salida serial USB")
    show_code(
        '''pico_enable_stdio_usb(pico_app 1)
pico_enable_stdio_uart(pico_app 0)
target_link_libraries(pico_app pico_stdlib)''',
        language="cmake",
    )
    show_code(
        '''stdio_init_all();
printf("Firmware activo\\n");''',
        language="cpp",
    )
    with st.expander("CMake mínimo de un proyecto"):
        show_code(
            '''cmake_minimum_required(VERSION 3.13)
set(CMAKE_C_STANDARD 11)
set(CMAKE_CXX_STANDARD 17)
set(PICO_BOARD pico2_w CACHE STRING "Board type")

include(pico_sdk_import.cmake)
project(pico_app C CXX ASM)
pico_sdk_init()

add_executable(pico_app main.cpp)
target_link_libraries(pico_app pico_stdlib hardware_adc)
pico_enable_stdio_usb(pico_app 1)
pico_enable_stdio_uart(pico_app 0)
pico_add_extra_outputs(pico_app)''',
            language="cmake",
        )


def render_search_results(query: str) -> None:
    page_heading(
        "Búsqueda",
        f"Resultados para “{query}”",
        "Coincidencias en descripciones de periféricos y nombres de funciones del Pico SDK.",
    )
    normalized = query.casefold()
    matches = [
        (name, data)
        for name, data in PERIPHERALS.items()
        if normalized
        in " ".join(
            (
                name,
                data["group"],
                data["description"],
                data["theory"],
                data["pins"],
                data["library"],
                data["wire"],
                data["warning"],
                " ".join(data["resources"]),
                " ".join(function for function, _ in data["api"]),
            )
        ).casefold()
    ]
    api_matches = [row for row in SDK_API if normalized in " ".join(row).casefold()]
    if not matches and not api_matches:
        st.info("No hay coincidencias. Prueba con `i2c`, `gpio`, `adc`, `dma` o `uart`.")
        return
    for name, data in matches:
        with st.container(border=True):
            st.markdown(f"#### {name}")
            st.write(data["description"])
            st.caption(f"{data['library']} · {data['pins']}")
            show_code(data["code"], language="cpp")
    for function, description, example in api_matches:
        with st.expander(f"`{function}` · {description}"):
            show_code(example, language="cpp")


with st.sidebar:
    st.markdown("## :material/developer_board: Pico 2 W")
    st.caption("Manual práctico de hardware y firmware")
    st.markdown("")
    section = st.radio(
        "Contenido",
        options=NAVIGATION,
        format_func=lambda item: f"{NAV_ICONS[item]}  {item}",
        key="section",
    )
    search_query = st.text_input(
        "Buscar en la guía",
        placeholder="GPIO, SPI, ADC, SVM…",
        key="global_search",
    )
    st.markdown("")
    st.caption("SDK C/C++ · RP2350 · CYW43439")

if search_query.strip():
    render_search_results(search_query.strip())
elif section == "Inicio":
    render_home()
elif section == "Arquitectura":
    render_architecture()
elif section == "Periféricos":
    render_peripherals()
elif section == "API del Pico SDK":
    render_sdk_api()
elif section == "Wi-Fi y Bluetooth":
    render_wireless()
elif section == "DSP, SVM y redes neuronales":
    render_dsp_ml()
else:
    render_build()

st.markdown("")
st.caption(
    "Documentación de aprendizaje; valida siempre las conexiones, los límites eléctricos "
    "y la compatibilidad de las APIs contra el datasheet y la versión del Pico SDK."
)
st.markdown(
    "[Pico SDK C/C++](https://www.raspberrypi.com/documentation/microcontrollers/c_sdk.html) · "
    "[Datasheet RP2350](https://datasheets.raspberrypi.com/rp2350/rp2350-datasheet.pdf) · "
    "[Ejemplos oficiales](https://github.com/raspberrypi/pico-examples) · "
    "[CMSIS-DSP](https://arm-software.github.io/CMSIS-DSP/latest/) · "
    "[CMSIS-NN](https://github.com/ARM-software/CMSIS-NN)"
)
