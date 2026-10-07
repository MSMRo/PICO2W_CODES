# Tutorial: Raspberry Pi Pico 2 W con el SDK C/C++

Este tutorial muestra cómo preparar, compilar y cargar programas C/C++ para la
**Raspberry Pi Pico 2 W** usando el **Raspberry Pi Pico SDK**. El repositorio
incluye un ejemplo funcional que alterna un LED externo y lee una entrada
analógica por USB:

- Código: [`adc_test1/adc_test1.cpp`](./adc_test1/adc_test1.cpp)
- Configuración CMake: [`adc_test1/CMakeLists.txt`](./adc_test1/CMakeLists.txt)

El ejemplo del repositorio está configurado para la placa `pico2_w` y Pico SDK
2.3.1. El SDK proporciona funciones de bajo nivel para GPIO, ADC, temporizadores,
USB y el chip inalámbrico CYW43439 de la Pico 2 W.

## 1. Materiales

- Raspberry Pi Pico 2 W y un cable USB de datos.
- Una computadora con CMake, Ninja y la cadena de herramientas ARM para
  RP2350.
- Para el ejemplo GPIO: LED externo, resistencia de 220–1 kΩ y cables.
- Para el ejemplo ADC: una señal analógica dentro del rango permitido.

> **Seguridad eléctrica:** los GPIO de la Pico 2 W trabajan a 3.3 V y no son
> tolerantes a 5 V. No conectes 5 V a un GPIO ni excedas 3.3 V en una entrada
> ADC. Usa una resistencia en serie con cualquier LED externo.

## 2. Preparar el entorno

### Opción A: Visual Studio Code

La configuración de este repositorio está preparada para la extensión
**Raspberry Pi Pico** de VS Code. Instala esa extensión y sigue su asistente
para instalar el SDK y las herramientas. Abre la carpeta del ejemplo
`adc_test1` como proyecto Pico y selecciona la placa **Pico 2 W** (`pico2_w`).

La extensión puede encargarse de configurar CMake, compilar y cargar el
programa. Los archivos `.vscode` del ejemplo incluyen tareas de compilación,
carga y depuración para el entorno Pico instalado en Windows.

### Opción B: CMake desde la terminal

Instala CMake, Ninja, Git y el toolchain ARM que requiere el Pico SDK. Descarga
o instala el Raspberry Pi Pico SDK y configura la variable de entorno
`PICO_SDK_PATH` para que apunte a su carpeta. El archivo
`adc_test1/pico_sdk_import.cmake` importa el SDK durante la configuración.

Desde la raíz del repositorio, configura y compila:

```powershell
cmake -S adc_test1 -B adc_test1/build -DPICO_BOARD=pico2_w -G Ninja
cmake --build adc_test1/build
```

Si las herramientas no están en `PATH`, añade sus directorios o usa la
extensión Pico de VS Code, que instala y configura CMake, Ninja y el toolchain.
El archivo resultante para cargar es `adc_test1/build/adc_test1.uf2`.

## 3. Cargar el programa a la placa

1. Desconecta la Pico 2 W.
2. Mantén pulsado **BOOTSEL** mientras conectas el cable USB.
3. Suelta el botón. La placa aparecerá como una unidad USB.
4. Copia el archivo `.uf2` generado a esa unidad.
5. La placa se reiniciará y ejecutará el programa.

También puedes usar la tarea **Run Project** de VS Code para cargar con
`picotool`, o **Flash** si tienes un depurador compatible conectado.

## 4. Estructura mínima de un proyecto

Un proyecto del SDK normalmente incluye un archivo CMake, un archivo de
importación del SDK (`pico_sdk_import.cmake`) y el código fuente.
El CMakeLists del ejemplo del repositorio, simplificado, tiene esta forma:

```cmake
cmake_minimum_required(VERSION 3.13)

set(CMAKE_C_STANDARD 11)
set(CMAKE_CXX_STANDARD 17)
set(PICO_BOARD pico2_w CACHE STRING "Board type")

include(pico_sdk_import.cmake)
project(mi_proyecto C CXX ASM)
pico_sdk_init()

add_executable(mi_proyecto main.cpp)
target_link_libraries(mi_proyecto pico_stdlib)

pico_enable_stdio_usb(mi_proyecto 1)
pico_enable_stdio_uart(mi_proyecto 0)
pico_add_extra_outputs(mi_proyecto)
```

El ejecutable debe enlazarse con las bibliotecas del SDK que utiliza. Por
ejemplo, para el ADC se agrega `hardware_adc`; para Wi-Fi se agrega la
biblioteca de arquitectura CYW43 correspondiente. `pico_add_extra_outputs`
genera, entre otros archivos, el UF2 que se carga en la placa.

## 5. Ejemplo: alternar un LED externo

Conecta un LED en serie con una resistencia entre **GPIO 15** y GND (ánodo del
LED hacia el GPIO, cátodo hacia la resistencia y GND). No conectes el LED
directamente entre el pin y GND.

```cpp
#include "pico/stdlib.h"

constexpr uint LED_PIN = 15;

int main() {
    gpio_init(LED_PIN);
    gpio_set_dir(LED_PIN, GPIO_OUT);

    while (true) {
        gpio_put(LED_PIN, 1);
        sleep_ms(500);
        gpio_put(LED_PIN, 0);
        sleep_ms(500);
    }
}
```

El código configura el pin como salida y lo enciende y apaga cada medio
segundo. En C++ se pueden usar directamente las funciones C del SDK.

## 6. Ejemplo del repositorio: leer el ADC

`adc_test1/adc_test1.cpp` combina el LED externo con el ADC y envía los datos
por USB Serial. Para probarlo:

1. Conecta una tensión analógica de **0 a 3.3 V** a GPIO 26 (ADC0).
2. Conecta el LED externo con resistencia a GPIO 15.
3. Compila y carga `adc_test1/build/adc_test1.uf2`.
4. Abre un monitor serial USB a **115200 baudios** y reinicia la placa.

La lectura del ADC es un valor de 12 bits (`0` a `4095`). El ejemplo calcula
una tensión aproximada multiplicando el valor por `3.3 / 4096`; la tensión
calculada es orientativa y depende de la referencia y alimentación reales.
Nunca apliques más de 3.3 V a GPIO 26.

Fragmento esencial de la lectura:

```cpp
#include "hardware/adc.h"

adc_init();
adc_gpio_init(26);      // GPIO 26 = ADC0
adc_select_input(0);

uint16_t lectura = adc_read();
float voltaje_aproximado = lectura * (3.3f / 4096.0f);
```

En el CMake del ejemplo, `hardware_adc` está enlazado para proporcionar esas
funciones.

## 7. Ejemplo: LED integrado y conexión Wi-Fi

El LED integrado de la Pico 2 W está controlado por el chip inalámbrico
CYW43439; no equivale a un GPIO de usuario como GPIO 15. Para acceder a él y al
Wi-Fi, enlaza la arquitectura CYW43 de lwIP en el `CMakeLists.txt`:

```cmake
target_link_libraries(mi_proyecto
    pico_stdlib
    pico_cyw43_arch_lwip_threadsafe_background
)
```

El siguiente programa conecta la placa a una red de 2.4 GHz y hace parpadear
el LED integrado. Sustituye los valores de ejemplo por los de tu red; no
publiques ni subas contraseñas reales al repositorio.

```cpp
#include <stdio.h>
#include "pico/stdlib.h"
#include "pico/cyw43_arch.h"

constexpr char WIFI_SSID[] = "NOMBRE_DE_TU_RED";
constexpr char WIFI_PASSWORD[] = "CONTRASENA_DE_TU_RED";

int main() {
    stdio_init_all();

    if (cyw43_arch_init() != 0) {
        printf("No se pudo inicializar el chip Wi-Fi\n");
        return 1;
    }

    cyw43_arch_enable_sta_mode();
    int resultado = cyw43_arch_wifi_connect_timeout_ms(
        WIFI_SSID,
        WIFI_PASSWORD,
        CYW43_AUTH_WPA2_AES_PSK,
        30000
    );

    if (resultado != 0) {
        printf("No se pudo conectar a la red Wi-Fi (codigo %d)\n", resultado);
        cyw43_arch_deinit();
        return 1;
    }

    printf("Conectado a Wi-Fi\n");
    while (true) {
        cyw43_arch_gpio_put(CYW43_WL_GPIO_LED_PIN, 1);
        sleep_ms(500);
        cyw43_arch_gpio_put(CYW43_WL_GPIO_LED_PIN, 0);
        sleep_ms(500);
    }
}
```

Activa la salida USB Serial en CMake para ver los mensajes del programa:

```cmake
pico_enable_stdio_usb(mi_proyecto 1)
pico_enable_stdio_uart(mi_proyecto 0)
```

Usa un archivo local no versionado para las credenciales en un proyecto real,
o un método de configuración apropiado para tu aplicación. Una red abierta,
WPA diferente o una región inalámbrica con requisitos particulares puede
necesitar una configuración de autenticación o CYW43 distinta.

## 8. Salida serial USB

Para enviar mensajes al monitor serial, inicializa la salida estándar:

```cpp
#include <stdio.h>
#include "pico/stdlib.h"

int main() {
    stdio_init_all();
    sleep_ms(2000); // Da tiempo a abrir el monitor serial USB
    printf("Hola desde la Pico 2 W\n");
}
```

Comprueba que USB está habilitado para el ejecutable:

```cmake
pico_enable_stdio_usb(mi_proyecto 1)
pico_enable_stdio_uart(mi_proyecto 0)
```

## 9. Periféricos del RP2350 y la Pico 2 W

La Pico 2 W combina el microcontrolador **RP2350** con el chip inalámbrico
**CYW43439**. El SDK incluye APIs para los periféricos integrados del RP2350;
Wi-Fi y Bluetooth se manejan mediante bibliotecas del CYW43439. Esta tabla
resume los periféricos más útiles y las bibliotecas habituales:

| Periférico | Para qué sirve | Biblioteca / cabecera |
|---|---|---|
| GPIO | Entradas y salidas digitales | `pico_stdlib`, `pico/stdlib.h` |
| UART | Comunicación serial asíncrona | `hardware_uart`, `hardware/uart.h` |
| I2C | Sensores y dispositivos de dos cables | `hardware_i2c`, `hardware/i2c.h` |
| SPI | Pantallas, memorias y dispositivos rápidos | `hardware_spi`, `hardware/spi.h` |
| PWM | Control de brillo, motores y señales periódicas | `hardware_pwm`, `hardware/pwm.h` |
| ADC | Lectura de señales analógicas | `hardware_adc`, `hardware/adc.h` |
| Temporizadores | Medición y tareas periódicas | `hardware_timer`, `pico/time.h` |
| Interrupciones | Reaccionar a eventos de GPIO y hardware | `hardware_irq`, `hardware/gpio.h` |
| DMA | Transferencias de datos con poca intervención de CPU | `hardware_dma`, `hardware/dma.h` |
| PIO | Protocolos y señales digitales personalizadas | `hardware_pio`, `hardware/pio.h` |
| Watchdog | Reiniciar el sistema si el programa se bloquea | `hardware_watchdog`, `hardware/watchdog.h` |
| Flash | Almacenamiento persistente en la memoria del programa | `hardware_flash`, `hardware/flash.h` |
| RTC | Reloj/calendario con fecha y hora | `hardware_rtc`, `hardware/rtc.h` |
| Multicore | Ejecutar tareas en los dos núcleos Cortex-M33 | `pico_multicore`, `pico/multicore.h` |
| Interpolador | Operaciones rápidas de enteros y procesamiento numérico | `hardware_interp`, `hardware/interp.h` |
| HSTX | Transmisión serie de alta velocidad; base de ejemplos de vídeo | `hardware_hstx`, `hardware/hstx.h` |
| USB | Serial USB y funciones USB del dispositivo | `pico_stdio_usb` / `pico_stdlib` |
| Wi-Fi | Red inalámbrica de 2.4 GHz | `pico_cyw43_arch_*` |
| Bluetooth LE | Conexiones BLE | BTstack incluido con el SDK |

Los ejemplos de esta sección son fragmentos para incorporar a un proyecto
inicializado con `pico_sdk_init()`. Agrega al `target_link_libraries` del
ejecutable las bibliotecas `hardware_*` que correspondan. Por ejemplo:

```cmake
target_link_libraries(mi_proyecto
    pico_stdlib
    hardware_uart
    hardware_i2c
    hardware_spi
    hardware_pwm
    hardware_adc
    hardware_dma
    hardware_timer
    hardware_irq
    hardware_pio
    hardware_watchdog
    hardware_flash
    hardware_rtc
    hardware_interp
    hardware_hstx
    pico_multicore
)
```

En un proyecto normal incluye solamente las bibliotecas que utilizas. Los
GPIO tienen funciones alternativas: el pin asignado a UART, I2C, SPI o PWM
debe configurarse para esa función y las combinaciones disponibles dependen
del periférico. Consulta el pinout oficial de la Pico 2 W antes de cablear.
El mismo GPIO no puede usarse simultáneamente para dos funciones.

### I2C: leer un registro de un sensor

Ejemplo para I2C0 en GPIO 4 (SDA) y GPIO 5 (SCL). Conecta también GND entre
la placa y el dispositivo. El código lee dos bytes desde el registro `0x00`
del dispositivo de ejemplo en la dirección `0x68`; cambia dirección y
registro según la hoja de datos del sensor.

```cpp
#include <cstddef>
#include "pico/stdlib.h"
#include "hardware/i2c.h"

constexpr uint SDA_PIN = 4;
constexpr uint SCL_PIN = 5;
constexpr uint8_t SENSOR_ADDR = 0x68;

void iniciar_i2c() {
    i2c_init(i2c0, 100 * 1000); // 100 kHz
    gpio_set_function(SDA_PIN, GPIO_FUNC_I2C);
    gpio_set_function(SCL_PIN, GPIO_FUNC_I2C);
    gpio_pull_up(SDA_PIN);
    gpio_pull_up(SCL_PIN);
}

bool leer_registro(uint8_t registro, uint8_t *datos, std::size_t cantidad) {
    int escrito = i2c_write_blocking(
        i2c0, SENSOR_ADDR, &registro, 1, true
    ); // true: conservar el bus para la lectura repetida
    if (escrito != 1) {
        return false;
    }

    int leido = i2c_read_blocking(
        i2c0, SENSOR_ADDR, datos, cantidad, false
    );
    return leido == static_cast<int>(cantidad);
}
```

Algunos módulos ya incorporan resistencias pull-up; no añadas otras sin
comprobar el esquema del módulo. Los pull-up del GPIO pueden no ser adecuados
para todas las velocidades o longitudes de cable.

### SPI: transferir un byte con un dispositivo

Ejemplo para SPI0: GPIO 16 (MISO), GPIO 19 (MOSI), GPIO 18 (SCK) y GPIO 17
(CS manual). Conecta el periférico, GND común y alimentación compatible de
3.3 V. El byte enviado y el recibido dependen del protocolo del dispositivo.

```cpp
#include "pico/stdlib.h"
#include "hardware/spi.h"

constexpr uint MISO_PIN = 16;
constexpr uint CS_PIN = 17;
constexpr uint SCK_PIN = 18;
constexpr uint MOSI_PIN = 19;

void iniciar_spi() {
    spi_init(spi0, 1 * 1000 * 1000); // 1 MHz
    gpio_set_function(MISO_PIN, GPIO_FUNC_SPI);
    gpio_set_function(SCK_PIN, GPIO_FUNC_SPI);
    gpio_set_function(MOSI_PIN, GPIO_FUNC_SPI);

    gpio_init(CS_PIN);
    gpio_set_dir(CS_PIN, GPIO_OUT);
    gpio_put(CS_PIN, 1);
    spi_set_format(
        spi0, 8, SPI_CPOL_0, SPI_CPHA_0, SPI_MSB_FIRST
    );
}

uint8_t transferir_spi(uint8_t byte_enviado) {
    uint8_t byte_recibido = 0;
    gpio_put(CS_PIN, 0);
    spi_write_read_blocking(spi0, &byte_enviado, &byte_recibido, 1);
    gpio_put(CS_PIN, 1);
    return byte_recibido;
}
```

Configura frecuencia, modo SPI (polaridad y fase), tamaño de palabra y
secuencia de comandos de acuerdo con la hoja de datos del dispositivo.

### UART: transmitir y recibir por pines

UART0 puede usar GPIO 0 (TX) y GPIO 1 (RX) en esta configuración. Cruza TX
con RX en el otro equipo y comparte GND. No conectes niveles de señal de 5 V.

```cpp
#include "pico/stdlib.h"
#include "hardware/uart.h"

void iniciar_uart() {
    uart_init(uart0, 115200);
    gpio_set_function(0, GPIO_FUNC_UART); // TX
    gpio_set_function(1, GPIO_FUNC_UART); // RX
    uart_set_format(uart0, 8, 1, UART_PARITY_NONE);
}

void enviar_uart(const char *mensaje) {
    uart_puts(uart0, mensaje);
}

char recibir_uart() {
    return uart_getc(uart0); // Espera hasta recibir un carácter
}
```

UART por GPIO es una interfaz distinta de la salida **USB Serial** configurada
en las secciones anteriores.

### PWM: variar el brillo de un LED

PWM produce una señal digital con ciclo de trabajo variable. En este ejemplo,
GPIO 15 maneja un LED externo con resistencia. `wrap` establece el periodo y
`level` el tiempo en nivel alto dentro de ese periodo.

```cpp
#include "pico/stdlib.h"
#include "hardware/pwm.h"

constexpr uint PWM_PIN = 15;

void iniciar_pwm() {
    gpio_set_function(PWM_PIN, GPIO_FUNC_PWM);
    uint slice = pwm_gpio_to_slice_num(PWM_PIN);
    pwm_config config = pwm_get_default_config();
    pwm_config_set_wrap(&config, 999);
    pwm_init(slice, &config, false);
    pwm_set_gpio_level(PWM_PIN, 0);
    pwm_set_enabled(slice, true);
}

void ajustar_brillo(uint16_t nivel) {
    // El nivel válido con wrap=999 es de 0 a 1000.
    pwm_set_gpio_level(PWM_PIN, nivel > 1000 ? 1000 : nivel);
}
```

Llama a `ajustar_brillo()` con valores entre 0 (apagado) y 1000 (máximo).
Para un motor usa un driver apropiado; no conectes el motor directamente al
GPIO.

### Temporizador: ejecutar una acción periódicamente

Los temporizadores del SDK permiten ejecutar un callback repetitivo sin
bloquear el bucle principal. El valor negativo de intervalo indica que los
periodos se calculan desde el instante real de cada llamada.

```cpp
#include "pico/stdlib.h"
#include "pico/time.h"

constexpr uint LED_PIN = 15;

bool callback_temporizador(repeating_timer_t *timer) {
    (void)timer;
    gpio_xor_mask(1u << LED_PIN);
    return true; // true mantiene activo el temporizador
}

int main() {
    gpio_init(LED_PIN);
    gpio_set_dir(LED_PIN, GPIO_OUT);

    repeating_timer_t temporizador;
    add_repeating_timer_ms(-500, callback_temporizador, nullptr, &temporizador);
    while (true) {
        tight_loop_contents();
    }
}
```

Mantén los callbacks breves. Para operaciones que tarden mucho, marca el
evento en el callback y procesa el trabajo en el bucle principal.

### Interrupción: detectar un botón

Conecta un botón entre GPIO 14 y GND. El pull-up interno mantiene el pin en
nivel alto cuando el botón está suelto; al pulsarlo se produce un flanco
descendente. En un proyecto real añade antirrebote por software o hardware.

```cpp
#include "pico/stdlib.h"

constexpr uint BUTTON_PIN = 14;
volatile bool boton_pulsado = false;

void callback_gpio(uint gpio, uint32_t eventos) {
    if (gpio == BUTTON_PIN && (eventos & GPIO_IRQ_EDGE_FALL)) {
        boton_pulsado = true;
    }
}

void iniciar_boton() {
    gpio_init(BUTTON_PIN);
    gpio_set_dir(BUTTON_PIN, GPIO_IN);
    gpio_pull_up(BUTTON_PIN);
    gpio_set_irq_enabled_with_callback(
        BUTTON_PIN, GPIO_IRQ_EDGE_FALL, true, &callback_gpio
    );
}
```

No uses `printf`, esperas largas ni operaciones complejas dentro de una ISR.
En el programa principal comprueba y borra `boton_pulsado` para procesar el
evento fuera de la interrupción.

### DMA: copiar datos sin bloquear la CPU

DMA resulta útil para transferencias repetitivas o bloques de datos. Este
ejemplo copia cuatro palabras entre dos arreglos en RAM:

```cpp
#include "hardware/dma.h"

void copiar_con_dma() {
    uint32_t origen[] = {10, 20, 30, 40};
    uint32_t destino[4] = {};
    int canal = dma_claim_unused_channel(true);

    dma_channel_config config = dma_channel_get_default_config(canal);
    channel_config_set_transfer_data_size(&config, DMA_SIZE_32);
    channel_config_set_read_increment(&config, true);
    channel_config_set_write_increment(&config, true);

    dma_channel_configure(
        canal, &config, destino, origen, 4, true
    );
    dma_channel_wait_for_finish_blocking(canal);
    dma_channel_unclaim(canal);
}
```

Para liberar el canal en todos los caminos de error, en aplicaciones
complejas gestiona su propiedad y limpieza explícitamente. DMA también puede
alimentar periféricos, pero la configuración de DREQ y el tamaño deben
coincidir con el periférico.

### PIO: generar una señal digital personalizada

PIO permite implementar protocolos y temporizaciones que no cubren los
periféricos estándar. Guarda este programa en `blink.pio`:

```pio
.program blink
.wrap_target
    set pins, 1 [31]
    set pins, 0 [31]
.wrap
```

El programa genera una onda cuadrada rápida para observar con un analizador
lógico u osciloscopio; no es un parpadeo visible a simple vista. Genera el
encabezado y enlaza PIO desde CMake:

```cmake
target_link_libraries(mi_proyecto pico_stdlib hardware_pio)
pico_generate_pio_header(mi_proyecto
    ${CMAKE_CURRENT_LIST_DIR}/blink.pio
)
```

Inicialización de la máquina de estados para GPIO 15:

```cpp
#include "hardware/pio.h"
#include "blink.pio.h"

void iniciar_blink_pio() {
    constexpr uint PIN = 15;
    PIO pio = pio0;
    uint offset = pio_add_program(pio, &blink_program);
    uint sm = pio_claim_unused_sm(pio, true);

    pio_gpio_init(pio, PIN);
    pio_sm_set_consecutive_pindirs(pio, sm, PIN, 1, true);
    pio_sm_config config = blink_program_get_default_config(offset);
    sm_config_set_set_pins(&config, PIN, 1);
    pio_sm_init(pio, sm, offset, &config);
    pio_sm_set_enabled(pio, sm, true);
}
```

La frecuencia del programa PIO depende del divisor de reloj de la máquina de
estados; ajusta el divisor con `sm_config_set_clkdiv()` si necesitas otro
periodo.

### Watchdog: recuperarse de un bloqueo

El watchdog reinicia el microcontrolador si no se alimenta dentro del plazo.
Solo úsalo cuando el programa pueda determinar que sigue funcionando
correctamente; no lo alimentes ciegamente desde una interrupción.

```cpp
#include "hardware/watchdog.h"

void iniciar_watchdog() {
    watchdog_enable(5000, true); // Reinicio tras 5 segundos sin actualización
}

void tarea_principal() {
    // Ejecutar aquí trabajo y comprobar que el sistema está sano.
    watchdog_update();
}
```

### RTC: fecha y hora

El RTC del RP2350 puede mantener fecha y hora mientras la placa está
alimentada. Inicialízalo con una fecha/hora válida; si necesitas conservar
la hora al quitar alimentación, añade un RTC externo con batería.

```cpp
#include "hardware/rtc.h"

void iniciar_rtc() {
    rtc_init();
    datetime_t ahora{};
    ahora.year = 2026;
    ahora.month = 10;
    ahora.day = 6;
    ahora.dotw = 2; // Día de la semana: 0 = domingo
    ahora.hour = 12;
    ahora.min = 0;
    ahora.sec = 0;
    rtc_set_datetime(&ahora);
}

bool leer_rtc(datetime_t *ahora) {
    return rtc_get_datetime(ahora);
}
```

### Multicore: ejecutar trabajo en el segundo núcleo

El RP2350 tiene dos núcleos Cortex-M33. `pico_multicore` permite lanzar una
función en el núcleo 1; usa colas, mutexes o primitivas de sincronización del
SDK para compartir datos entre ambos núcleos.

```cpp
#include "pico/multicore.h"
#include "pico/stdlib.h"

void tarea_nucleo_1() {
    while (true) {
        // Trabajo independiente del núcleo principal.
        tight_loop_contents();
    }
}

int main() {
    multicore_launch_core1(tarea_nucleo_1);
    while (true) {
        // Trabajo del núcleo 0.
        tight_loop_contents();
    }
}
```

### Flash: almacenamiento persistente

El SDK ofrece `flash_range_erase()` y `flash_range_program()` en
`hardware/flash.h`. La Flash se borra por sectores y se programa por páginas;
los datos deben estar alineados y hay que reservar una región para ellos en el
mapa de memoria. No uses offsets ocupados por el firmware ni intentes borrar
la Flash mientras se ejecuta código desde ella. Consulta el ejemplo oficial
`flash_program` antes de escribir datos persistentes.

### Interpolador y HSTX

- **Interpolador:** acelerador de operaciones sobre enteros, útil en gráficos,
  tablas de consulta y cálculos de alto rendimiento. Su configuración es
  específica del problema; consulta los ejemplos `interp` del SDK.
- **HSTX:** periférico de transmisión de alta velocidad del RP2350. Se usa,
  por ejemplo, en diseños de vídeo digital como DVI; requiere conocer el
  protocolo y el cableado. Consulta los ejemplos oficiales de HSTX/DVI antes
  de conectarlo a una pantalla.

### USB y conectividad inalámbrica

- **USB:** el uso más sencillo en este tutorial es USB Serial mediante
  `stdio_init_all()` y `pico_enable_stdio_usb(mi_proyecto, 1)`. El SDK también
  integra TinyUSB para implementar dispositivos USB personalizados.
- **Wi-Fi:** utiliza el chip CYW43439 y la arquitectura `pico_cyw43_arch_*`;
  el ejemplo anterior conecta a una red y acciona el LED integrado.
- **Bluetooth LE:** la Pico 2 W incluye Bluetooth LE a través del CYW43439.
  El SDK incluye BTstack; selecciona un ejemplo BLE oficial compatible con la
  versión del SDK para ver el perfil, transporte y bibliotecas que requiere.

## 10. DSP con CMSIS-DSP

El **RP2350** de la Pico 2 W usa un Cortex-M33 con instrucciones DSP, pero no
incluye las extensiones vectoriales Helium/MVE de los Cortex-M55/M85. CMSIS-DSP
ofrece operaciones matemáticas, filtros, transformadas, estadísticas y otras
funciones optimizadas para Cortex-M. CMSIS-DSP es una biblioteca adicional:
no forma parte del Pico SDK.

### Integrar CMSIS-DSP con CMake

Obtén las bibliotecas oficiales CMSIS-DSP y CMSIS-Core, y CMSIS-NN si también
usarás redes neuronales. Puedes guardarlas bajo `external/` o en otra ubicación
no versionada. El directorio `CMSIS_6/CMSIS/Core` debe contener `Include/`
para la ruta mostrada abajo. Selecciona versiones compatibles entre sí y con
tu toolchain.

Después de `pico_sdk_init()` y de crear el ejecutable, añade CMSIS-DSP:

```cmake
set(CMSISCORE "${CMAKE_CURRENT_LIST_DIR}/external/CMSIS_6/CMSIS/Core"
    CACHE PATH "Directorio de CMSIS-Core que contiene Include/")
add_subdirectory(external/CMSIS-DSP/Source)
target_compile_definitions(CMSISDSP PUBLIC ARM_MATH_DSP)

target_link_libraries(mi_proyecto PRIVATE
    pico_stdlib
    CMSISDSP
)
```

`CMSISCORE` debe apuntar al directorio `CMSIS/Core` (el que contiene
`Include/`); el CMake de CMSIS-DSP usa `CMSISCORE/Include`. Si las bibliotecas
están fuera del árbol del proyecto, ajusta las rutas. En el Pico 2 W, compila
para el objetivo Arm Cortex-M33 de la placa; no habilites `ARM_MATH_MVEF`,
`ARM_MATH_MVEI` ni Helium, ya que el M33 no implementa MVE. En aplicaciones
con requisitos de tiempo real, compara las opciones de optimización del
compilador y mide el rendimiento del firmware final.

### Ejemplo: filtrar muestras con FIR

Este filtro FIR pasa-bajos promedia cinco muestras. Procesa bloques de ocho
muestras y conserva el estado entre llamadas; para un sensor real, reemplaza
el arreglo de entrada por las muestras del ADC u otro periférico.

```cpp
#include "arm_math.h"

constexpr uint32_t NUM_TAPS = 5;
constexpr uint32_t BLOCK_SIZE = 8;

const float32_t coeficientes[NUM_TAPS] = {
    0.2f, 0.2f, 0.2f, 0.2f, 0.2f
};
float32_t estado[NUM_TAPS + BLOCK_SIZE - 1] = {};

arm_fir_instance_f32 filtro{};

void iniciar_filtro() {
    arm_fir_init_f32(
        &filtro, NUM_TAPS, coeficientes, estado, BLOCK_SIZE
    );
}

void filtrar_bloque(
    const float32_t entrada[BLOCK_SIZE],
    float32_t salida[BLOCK_SIZE]
) {
    arm_fir_f32(&filtro, entrada, salida, BLOCK_SIZE);
}
```

CMSIS-DSP también ofrece funciones de propósito general, por ejemplo producto
escalar (`arm_dot_prod_f32`), FFT (`arm_rfft_fast_f32`), biquad
(`arm_biquad_cascade_df1_f32`), estadística (`arm_mean_f32`) y funciones
trigonométricas (`arm_sin_f32`). Consulta la documentación para los formatos
Q7/Q15/Q31 y los requisitos de memoria de cada función.

```cpp
#include "arm_math.h"

float32_t producto_escalar(
    const float32_t *a,
    const float32_t *b,
    uint32_t cantidad
) {
    float32_t resultado = 0.0f;
    arm_dot_prod_f32(a, b, cantidad, &resultado);
    return resultado;
}
```

## 11. Clasificador SVM con CMSIS-DSP

CMSIS-DSP incluye predictores **SVM binarios** lineales, polinomiales, RBF y
sigmoidales. No entrena el modelo: entrena el clasificador fuera de la Pico
(por ejemplo, en Python), y exporta sus clases, vectores de soporte,
coeficientes duales, intercepto y parámetros del kernel. El siguiente ejemplo
usa un modelo lineal diminuto ilustrativo; reemplaza los arreglos y el
intercepto por los parámetros exportados de tu SVM entrenado.

```cpp
#include "arm_math.h"

constexpr uint32_t NUM_SUPPORT_VECTORS = 1;
constexpr uint32_t FEATURE_COUNT = 2;

const float32_t support_vectors[NUM_SUPPORT_VECTORS * FEATURE_COUNT] = {
    1.0f, 0.0f
};
const float32_t dual_coefficients[NUM_SUPPORT_VECTORS] = {1.0f};
const int32_t class_ids[2] = {0, 1};

arm_svm_linear_instance_f32 svm{};

void iniciar_svm() {
    arm_svm_linear_init_f32(
        &svm,
        NUM_SUPPORT_VECTORS,
        FEATURE_COUNT,
        0.0f, // intercepto del ejemplo
        dual_coefficients,
        support_vectors,
        class_ids
    );
}

int32_t clasificar(const float32_t caracteristicas[FEATURE_COUNT]) {
    int32_t clase = 0;
    arm_svm_linear_predict_f32(&svm, caracteristicas, &clase);
    return clase;
}
```

Las características de entrada deben tener el mismo orden, normalización y
escalado usados durante el entrenamiento. La salida es una de las dos
etiquetas de `class_ids`, no la distancia al hiperplano. En SVM no lineales,
los vectores de soporte consumen RAM proporcional a
`cantidad_de_vectores × cantidad_de_características`; verifica memoria y
latencia con el modelo real.

## 12. Redes neuronales con CMSIS-NN

**CMSIS-NN no es un clasificador SVM ni un cargador de modelos**: proporciona
operadores eficientes para ejecutar redes neuronales, normalmente int8, en
Cortex-M. Para correr un modelo completo, usa un runtime compatible como
TensorFlow Lite for Microcontrollers (TFLM) con los kernels CMSIS-NN habilitados,
o implementa la secuencia de operadores del modelo. Conversión, cuantización,
escalas, zero-points y pesos deben provenir del modelo exportado; no se deben
inventar para una red entrenada.

### Integrar CMSIS-NN

Añade el repositorio CMSIS-NN a tu proyecto y enlaza su target `cmsis-nn`.
Este ejemplo de CMake supone `external/CMSIS-NN` y debe ir después de la
inicialización del SDK (CMSIS-NN requiere CMake 3.21 o posterior):

```cmake
add_subdirectory(external/CMSIS-NN)

target_link_libraries(mi_proyecto PRIVATE
    pico_stdlib
    cmsis-nn
)
```

Las funciones se declaran en `arm_nnfunctions.h`. En el Cortex-M33 se eligen
las implementaciones C/DSP adecuadas al toolchain; CMSIS-NN reserva sus
optimizaciones MVE para procesadores que sí tengan Helium. Si usas TFLM,
configura también ese runtime y genera el modelo con operadores compatibles.

### Ejemplo: ejecutar una capa fully connected int8

El siguiente ejemplo es una capa artificial de dos entradas y dos salidas con
pesos identidad. Solo demuestra la llamada de una operación CMSIS-NN, no es
un modelo entrenado. Usa escala de requantización unitaria como ejemplo;
para una red real, sustituye dimensiones, pesos, biases, offsets, rango de
activación, `multiplier` y `shift` por los valores generados junto con el
modelo. `ctx` sin buffer es apropiado para la implementación Cortex-M33 con
DSP; consulta `arm_fully_connected_s8_get_buffer_size()` si cambias de núcleo
o configuración.

```cpp
#include <cstdint>
#include "arm_nnfunctions.h"

constexpr int32_t INPUTS = 2;
constexpr int32_t OUTPUTS = 2;

const int8_t entrada[INPUTS] = {20, -10};
const int8_t pesos[OUTPUTS * INPUTS] = {
    1, 0, // Neurona 0
    0, 1  // Neurona 1
};
const int32_t bias[OUTPUTS] = {0, 0};
int8_t salida[OUTPUTS] = {};

bool ejecutar_capa() {
    const cmsis_nn_context contexto{nullptr, 0};
    const cmsis_nn_fc_params parametros{
        0,  // input_offset (negativo del zero-point de entrada)
        0,  // filter_offset; pesos simetricos int8
        0,  // output_offset
        {-128, 127}
    };
    const cmsis_nn_per_tensor_quant_params cuantizacion{
        1073741824, // multiplier ilustrativo para una escala efectiva 1
        1           // shift
    };
    const cmsis_nn_dims entrada_dims{1, 1, 1, INPUTS};
    const cmsis_nn_dims pesos_dims{INPUTS, 1, 1, OUTPUTS};
    const cmsis_nn_dims bias_dims{1, 1, 1, OUTPUTS};
    const cmsis_nn_dims salida_dims{1, 1, 1, OUTPUTS};

    return arm_fully_connected_s8(
        &contexto,
        &parametros,
        &cuantizacion,
        &entrada_dims,
        entrada,
        &pesos_dims,
        pesos,
        &bias_dims,
        bias,
        &salida_dims,
        salida
    ) == ARM_CMSIS_NN_SUCCESS;
}
```

En modelos reales, los tensores int8 representan valores reales mediante
`real = (quantized - zero_point) * scale`. La aritmética de la capa depende de
esos parámetros; usa los metadatos del conversor/runtime y conserva el orden
de los pesos esperado por el operador. Revisa el código de retorno y valida
las salidas en el hardware contra la inferencia de referencia.

## 13. Solución de problemas

- **CMake no encuentra el SDK:** verifica que `PICO_SDK_PATH` apunte a la raíz
  del SDK y que `pico_sdk_import.cmake` esté junto al CMakeLists del proyecto.
- **La placa no aparece al cargar:** usa un cable USB de datos y mantén
  BOOTSEL pulsado mientras conectas la placa.
- **No aparece salida serial:** habilita stdio USB, abre el monitor de la Pico
  2 W y espera un par de segundos después de conectarla.
- **El ADC siempre muestra cero o valores inesperados:** confirma que la señal
  está conectada a GPIO 26, que comparte GND con la placa y que no supera 3.3 V.
- **Wi-Fi no conecta:** la Pico 2 W usa Wi-Fi de 2.4 GHz; verifica SSID,
  contraseña, alcance y modo de autenticación.

## 14. Referencias

- [Raspberry Pi Pico-series C/C++ SDK](https://www.raspberrypi.com/documentation/microcontrollers/c_sdk.html)
- [Raspberry Pi Pico 2 W](https://www.raspberrypi.com/products/raspberry-pi-pico-2-w/)
- [Ejemplos oficiales del Pico SDK](https://github.com/raspberrypi/pico-examples)
- [CMSIS-DSP](https://github.com/ARM-software/CMSIS-DSP)
- [CMSIS-DSP: documentación de funciones](https://arm-software.github.io/CMSIS-DSP/latest/)
- [CMSIS-NN](https://github.com/ARM-software/CMSIS-NN)
- [TensorFlow Lite for Microcontrollers](https://www.tensorflow.org/lite/microcontrollers)