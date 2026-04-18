// // testing name for reference: job_6341212_872.out

// #include <iostream>
// #include <filesystem>
// #include <fstream>
// #include <string>
// #include <map>

// namespace fs = std::filesystem;

// bool extract_model_id(const std::string &line, int &id)
// {
//     std::size_t pos = line.find("model_");
//     if (pos == std::string::npos)
//         return false;

//     pos += std::string("model_").size();
//     std::size_t end = pos;
//     while (end < line.size() && std::isdigit(static_cast<unsigned char>(line[end])))
//     {
//         ++end;
//     }

//     if (end == pos)
//     {
//         return false;
//     }
//     id = std::stoi(line.substr(pos, end - pos));
//     return true;
// }

// bool extract_body(const std::string &line, int &body)
// {
//     bool singlebody = line.find("/singlebody/") != std::string::npos;
//     bool twobody = line.find("/twobody/") != std::string::npos;

//     if (!(singlebody || twobody))
//     {
//         return false;
//     }
//     else
//     {
//         if (singlebody)
//         {
//             body = 1;
//         }
//         else
//         {
//             body = 2;
//         }
//         return true;
//     }
// }

// std::string get_new_name(const fs::path &filepath, std::map<std::pair<int, int>, int> &counts)
// {
//     std::ifstream file(filepath);

//     if (!file.is_open())
//     {
//         std::cerr << "Could not open file: " << filepath << "\n";
//         return std::to_string(9999999999);
//     }

//     std::string line;
//     int id;
//     int body;
//     int curr_count;
//     while (std::getline(file, line))
//     {
//         if (line.find("Processing JSON:") != std::string::npos)
//         {
//             if (!(extract_model_id(line, id) && extract_body(line, body)))
//             {
//                 std::cout << "WARNING: unable to read line [" << line << "]" << std::endl;
//                 return std::to_string(9999999999);
//             }
//             std::pair<int, int> key = std::make_pair(id, body);
//             if (counts.find(key) == counts.end())
//             {
//                 curr_count = 0;
//                 counts[key] = 1;
//             }
//             else
//             {
//                 curr_count = counts[key];
//                 counts[key] += 1;
//             }
//             return "model_" + std::to_string(id) + "_" + std::to_string(body) + "body_" + std::to_string(curr_count);
//         }
//     }

//     std::cout << "WARNING: unable to parse file [" << filepath << "]" << std::endl;
//     return std::to_string(9999999999);
// }

// int main()
// {
//     // UPDATE THIS to the path where your .out and .err files live
//     // fs::path logs_dir = "/scratch/seb9449/offsets_testing_thingi10k/offsets-thingi10k-test/bash_scripts/offsets_array/logs";
//     fs::path logs_dir = "/Users/seb9449/Desktop/offsets-thingi10k-test/test_data/test_logs";

//     if (!fs::exists(logs_dir) || !fs::is_directory(logs_dir))
//     {
//         std::cerr << "Error: Directory " << logs_dir << " does not exist.\n";
//         return 1;
//     }

//     std::map<std::pair<int, int>, int> counts;

//     std::cout << "Scanning for job_*.out and job_*.err files...\n";
//     int processed_count = 0;

//     for (const auto &entry : fs::directory_iterator(logs_dir))
//     {
//         if (!entry.is_regular_file())
//             continue;

//         std::string filename = entry.path().filename().string();
//         std::string ext = entry.path().extension().string();

//         // 1. Check if the file starts with "job_"
//         if (filename.find("job_") != 0)
//             continue;

//         // 2. Check if the extension is .out or .err
//         if (ext != ".out" && ext != ".err")
//             continue;

//         // 3. Extract the integers
//         std::string new_str = get_new_name(entry.path(), counts);
//         if (new_str != std::to_string(9999999999))
//         {
//             std::string new_filename = new_str + ext;
//             fs::path new_filepath = entry.path().parent_path() / new_filename;

//             try
//             {
//                 fs::rename(entry.path(), new_filepath);
//                 processed_count++;
//             }
//             catch (const fs::filesystem_error &e)
//             {
//                 std::cerr << "Error renaming " << filename << ": " << e.what() << std::endl;
//             }
//             std::cout << "\r" << processed_count;
//         }
//     }

//     std::cout << "Successfully renamed " << processed_count << " files.\n";
//     return 0;
// }