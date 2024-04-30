#define FMT_HEADER_ONLY

#include "event_loops.h"
#include "global_vars.h"
#include "http_service/oatpp_entry.h"
#include "model_utils.h"
#include "utils.h"

#include <cxxopts.hpp>
#include <fmt/core.h>
#include <nlohmann/json.hpp>
#include <spdlog/spdlog.h>

#include <chrono>
#include <filesystem>
#include <fstream>
#include <iostream>
#include <stdexcept>
#include <string>

using namespace std;
using json = nlohmann::json;

int main(int argc, char **argv) {
  install_signal_handler();
  string config_path;

  cxxopts::Options options(argv[0], "Inference service");
  // clang-format off
  options.add_options()
    ("h,help", "print help message")
    ("c,config-path", "JSON configuration file path", cxxopts::value<string>()->default_value(config_path));
  // clang-format on
  auto result = options.parse(argc, argv);
  if (result.count("help") || !result.count("config-path")) {
    std::cout << options.help() << "\n";
    return 0;
  }
  config_path = result["config-path"].as<std::string>();

  spdlog::set_pattern("%Y-%m-%d %T.%e | %7l | %5t | %v");
  spdlog::info("inference_service started");
  spdlog::info("Loading configurations from {}:", config_path);
  ifstream f(config_path);
  settings = json::parse(f);
  spdlog::info("{}", settings.dump(2));
  model_ids = settings.value("/inference/initial_model_ids"_json_pointer,
                             vector<string>{"0"});
  torch_script_serialization = settings.value(
      "/model/torch_script_serialization"_json_pointer, string(""));

  initialize_rest_api(
      settings.value("/inference/swagger/host"_json_pointer, "127.0.0.1"),
      settings.value("/inference/swagger/port"_json_pointer, 8000),
      settings.value("/inference/swagger/advertised_host"_json_pointer,
                     "http://127.0.0.1:8000"));

  thread thread_zeromq(zeromq_ev_loop);
  thread thread_inference(inference_ev_loop);
  if (thread_zeromq.joinable()) {
    thread_zeromq.join();
  }
  if (thread_inference.joinable()) {
    thread_inference.join();
  }
  finalize_rest_api();
  spdlog::info("inference_service exiting");
  return 0;
}
