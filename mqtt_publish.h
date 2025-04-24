#ifndef MQTT_PUBLISH_H
#define MQTT_PUBLISH_H

int publish_motion_event(const char *broker, const char *topic, const char *payload);

#endif // MQTT_PUBLISH_H
