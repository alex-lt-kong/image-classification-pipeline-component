#include "global_vars.h"

using namespace std;

volatile sig_atomic_t ev_flag = 0;

mutex image_queue_mtx;
mutex ext_program_mtx;
mutex swagger_mtx;
mutex models_mtx;
mutex model_ids_mtx;

const ssize_t gif_frame_count = 36;
const ssize_t inference_batch_size = 24;
const ssize_t pre_detection_size = 4;
const ssize_t image_queue_min_len =
    pre_detection_size + inference_batch_size + gif_frame_count;
const ssize_t image_queue_max_len = image_queue_min_len * 4;

deque<std::string> image_queue;

nlohmann::json settings;
vector<string> model_ids;
std::atomic<uint32_t> inference_interval_ms = 60000;
std::unordered_map<uint32_t, PercentileTracker<float>> pt_dict;

vector<torch::jit::script::Module> models;
std::string torch_script_serialization;