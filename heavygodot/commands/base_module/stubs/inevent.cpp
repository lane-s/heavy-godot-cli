
void $(audio_stream_classname)::trigger_$(lowercase_event_name)() {
    heavy_context->sendBangToReceiver(Heavy_Motor::Event::In::EventIn::$(event_name));
}