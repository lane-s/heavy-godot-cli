#include "register_types.h"
#include "class_db.h"
#include "$(module_name).h"

void register_$(module_name)_types() {
        ClassDB::register_class<$(audio_playback_classname)>();
        ClassDB::register_class<$(audio_stream_classname)>();
}

void unregister_$(module_name)_types() {
   //nothing to do here
}