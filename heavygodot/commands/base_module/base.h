#ifndef $(header_symbol)
#define $(header_symbol)

#include "reference.h"
#include "resource.h"
#include "servers/audio/audio_stream.h"
#include "HeavyContextInterface.hpp"
#include "$(patch_classname).hpp"

class $(audio_stream_classname) : public AudioStream {
    GDCLASS($(audio_stream_classname), AudioStream)
private:
    friend class $(audio_playback_classname);
    uint64_t pos;
    int mix_rate;
    bool stereo;
    int hz;
    HeavyContextInterface* heavy_context;
public:
    void start_event();
    void reset();
    void set_position(uint64_t pos);
    virtual Ref<AudioStreamPlayback> instance_playback();
    virtual String get_stream_name() const;
    void process_patch(float* pcm_buf, int frames);
    virtual float get_length() const { return 0; }
    $(audio_stream_classname)();
protected:
    static void _bind_methods();
};

class $(audio_playback_classname) : public AudioStreamPlayback {
    GDCLASS($(audio_playback_classname), AudioStreamPlayback)
    friend class $(audio_stream_classname);
private:
    enum{
        PCM_BUFFER_SIZE = 4096
    };
    enum {
        MIX_FRAC_BITS = 13,
        MIX_FRAC_LEN = (1 << MIX_FRAC_BITS),
        MIX_FRAC_MASK = MIX_FRAC_LEN - 1,
    };
    void * pcm_buffer;
    Ref<$(audio_stream_classname)> base;
    bool active;
public:
    virtual void start(float p_from_pos = 0.0);
    virtual void stop();
    virtual bool is_playing() const;
    virtual int get_loop_count() const;
    virtual float get_playback_position() const;
    virtual void seek(float p_time);
    virtual void mix(AudioFrame *p_buffer, float p_rate_scale, int p_frames);
    virtual float get_length() const; 
    $(audio_playback_classname)();
};

#endif