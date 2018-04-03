#include "register_types.h"
#include "class_db.h"
#include "$(module_name).h"

void register_$(module__types() {
        ClassDB::register_class<$(audio_playback_classname)>();
        ClassDB::register_class<$(audio_stream_classname)>();
}

void unregister_heavy_types() {
   //nothing to do here
}