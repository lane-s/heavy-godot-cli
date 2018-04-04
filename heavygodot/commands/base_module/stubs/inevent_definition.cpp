void $(audio_stream_classname)::$(method_name)() {
    heavy_context->sendBangToReceiver($(patch_classname)::Event::In::EventIn::$(event_name));
}