#include "$(module_name).h"
#include <iostream>

$(audio_stream_classname)::$(audio_stream_classname)()
    : mix_rate(44100) {
        heavy_context = new $(patch_classname)(mix_rate);
}

Ref<AudioStreamPlayback> $(audio_stream_classname)::instance_playback(){
    Ref<$(audio_playback_classname)> hv_playback;
    hv_playback.instance();
    hv_playback->base = Ref<$(audio_stream_classname)>(this);
    return hv_playback;
}
String $(audio_stream_classname)::get_stream_name() const {
    return "$(patch_classname)";
}

$(in_event_method_definitions)

void $(audio_stream_classname)::reset(){
    set_position(0);
}

void $(audio_stream_classname)::set_position(uint64_t p){
    pos = p;
}

void $(audio_stream_classname)::process_patch(float* pcm_buf, int size){
   heavy_context->processInline(NULL, pcm_buf, size); 
}

void $(audio_stream_classname)::_bind_methods(){
    ClassDB::bind_method(D_METHOD("reset"), &$(audio_stream_classname)::reset);
    ClassDB::bind_method(D_METHOD("get_stream_name"), &$(audio_stream_classname)::get_stream_name);
    $(in_event_binds)
}

$(audio_stream_classname)::~$(audio_stream_classname)(){
    delete heavy_context;
}

$(audio_playback_classname)::$(audio_playback_classname)(): active(false){
    buffer_size = BLOCK_SIZE * sizeof(float)

    AudioServer::get_singleton()->lock();
    pcm_buffer = AudioServer::get_singleton()->audio_data_alloc(buffer_size);
    zeromem(pcm_buffer, buffer_size);
    AudioServer::get_singleton()->unlock();
}

void $(audio_playback_classname)::stop(){
    active = false;
    base->reset();
}

void $(audio_playback_classname)::start(float p_from_pos){
    seek(p_from_pos);
    active = true;
}

void $(audio_playback_classname)::seek(float p_time){
    float max = get_length();
    if(p_time < 0){
        p_time = 0;
    }
    base->set_position(uint64_t(p_time * base->mix_rate) << MIX_FRAC_BITS);
}

void $(audio_playback_classname)::mix(AudioFrame *p_buffer, float p_rate, int p_frames){
    if(!active){
        for(int i = 0; i < p_frames; i++){
            p_buffer[i] = AudioFrame(0, 0);
        }
        return;
    }

    zeromem(pcm_buffer, buffer_size);
    float * buf = (float *)pcm_buffer;
    base->process_patch(buf, p_frames);

    for(int i = 0; i < p_frames; i++){
        float sample = buf[i];
        p_buffer[i] = AudioFrame(sample, sample);
    }
}

int $(audio_playback_classname)::get_loop_count() const {
    return 0;
}

float $(audio_playback_classname)::get_playback_position() const {
    return 0.0;
}

float $(audio_playback_classname)::get_length() const {
    return 0.0;
}

bool $(audio_playback_classname)::is_playing() const {
    return active;
}

$(audio_playback_classname)::~$(audio_playback_classname)(){
}