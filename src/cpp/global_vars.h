#ifndef VBCP_GLOBAL_VARS_H
#define VBCP_GLOBAL_VARS_H

#include "utils.h"

#include <ATen/ops/nonzero.h>
#include <nlohmann/json.hpp>

#include <deque>
#include <mutex>
#include <signal.h>
#include <string>
#include <unordered_map>
#include <vector>

extern volatile sig_atomic_t ev_flag;

extern std::mutex image_queue_mtx;
extern std::mutex ext_program_mtx;
extern std::mutex swagger_mtx;
extern std::mutex models_mtx;
extern std::mutex model_ids_mtx;

extern std::deque<std::string> image_queue;

extern const ssize_t gif_frame_count;
extern const ssize_t inference_batch_size;
extern const ssize_t pre_detection_size;
extern const ssize_t image_queue_min_len;
extern const ssize_t image_queue_max_len;
extern nlohmann::json settings;
extern std::vector<std::string> model_ids;

extern std::atomic<uint32_t> inference_interval_ms;
extern std::vector<std::string> model_ids;
extern std::unordered_map<uint32_t, PercentileTracker<float>> pt_dict;
extern std::vector<torch::jit::script::Module> models;

extern std::string torch_script_serialization;

#endif // VBCP_GLOBAL_VARS_H