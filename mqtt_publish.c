// MQTT publish stub (paho-mqtt-c or mosquitto)
#include "mqtt_publish.h"
#include <stdio.h>

int publish_motion_event(const char *broker, const char *topic, const char *payload) {
    // TODO: Implement MQTT publish using paho-mqtt-c or mosquitto
    printf("[MQTT] Would publish to %s topic %s: %s\n", broker, topic, payload);
    return 1;
}
