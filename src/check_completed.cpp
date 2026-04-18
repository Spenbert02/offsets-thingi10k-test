#include <iostream>
#include <filesystem>
#include <fstream>
#include <string>
#include <map>
#include <set>

namespace fs = std::filesystem;

const int EMPTY = 0;
const int INVERTED_INPUT = 1;
const int SPLIT_FAILED = 2;
const int TIMEOUT = 3;
const int COMPLETED = 4;
const int OTHER = 5;

bool get_job_ids(const std::string &fname, int &job_id, int &job_sub_id)
{
    return (std::sscanf(fname.c_str(), "job_%d_%d.out", &job_id, &job_sub_id) == 2);
}

bool get_model_info(std::string line, int &model_id, int &body)
{
    body = (line.find("/singlebody/") != std::string::npos) ? 1 : 2;

    std::size_t start = line.find("model_");
    if (start == std::string::npos)
    {
        return false;
    }

    start += 6;
    std::size_t end = start;
    while (end < line.size() && std::isdigit(static_cast<unsigned char>(line[end])))
    {
        ++end;
    }
    if (start == end)
    {
        return false;
    }
    model_id = std::stoi(line.substr(start, end - start));
    return true;
}

int main(int argc, char *argv[])
{
    if (argc != 2)
    {
        std::cerr << "Usage: " << argv[0] << "/path/to/log/directory" << std::endl;
        return 1;
    }

    std::string logs_dir_str = argv[1];
    fs::path logs_dir(logs_dir_str);
    if (!fs::is_directory(logs_dir))
    {
        std::cerr << "Logs directory '" << logs_dir << "' does not exist." << std::endl;
        return 1;
    }
    else
    {
        std::cout << "Using logs directory '" << logs_dir << "'" << std::endl;
    }

    // <model id, body> -----> <job id, job subid>
    std::map<std::pair<int, int>, std::pair<int, int>> most_recents;

    // track: empty input, inverted element in input, timeout, completed, other
    std::map<std::pair<int, int>, int> outcomes;

    int processed_count = 0;
    for (const auto &entry : fs::directory_iterator(logs_dir))
    {
        if (!entry.is_regular_file())
        {
            continue;
        }

        std::string fname = entry.path().filename().string();
        std::string ext = entry.path().extension().string();
        if (fname.find("job_") != 0)
        {
            continue;
        }
        if (ext != ".out")
        {
            continue;
        }

        std::string line;
        int classification = OTHER;

        // scan out file
        std::ifstream outfile(entry.path());
        if (!outfile.is_open())
        {
            std::cerr << "Could not open file: '" << entry.path() << "'" << std::endl;
            return 1;
        }

        // set model, job ids, skip if not newest for model id/body
        for (int i = 0; i < 3; i++)
        {
            std::getline(outfile, line);
        }
        int job_id, job_sub_id; // set job id and sub id
        int model_id, body;     // set model id and body
        if (!(get_job_ids(fname, job_id, job_sub_id) && get_model_info(line, model_id, body)))
        {
            std::cerr << "Could not extract job id or model id/body: '" << entry.path() << "'" << std::endl;
            return 1;
        }
        auto key = std::make_pair(model_id, body);
        if (most_recents.find(key) == most_recents.end())
        {
            most_recents[key] = std::make_pair(job_id, job_sub_id);
        }
        else
        {
            if (job_id < most_recents[key].first)
            {
                outfile.close();
                continue;
            }
            else
            {
                most_recents[key] = std::make_pair(job_id, job_sub_id);
            }
        }

        while (std::getline(outfile, line))
        {
            if (line.find("Empty input complex") != std::string::npos)
            {
                classification = EMPTY;
                break;
            }
            if (line.find("Inverted input element") != std::string::npos)
            {
                classification = INVERTED_INPUT;
                break;
            }
            if (line.find("tet split failed!") != std::string::npos)
            {
                classification = SPLIT_FAILED;
                break;
            }
            if (line.find("======= finish =========") != std::string::npos)
            {
                classification = COMPLETED;
                break;
            }
        }
        outfile.close();

        // check for timeout if need be
        if (classification == OTHER)
        {
            fs::path errpath = entry.path();
            errpath.replace_extension(".err");
            std::ifstream errfile(errpath);
            if (!errfile.is_open())
            {
                std::cerr << "Could not open file: '" << errpath << "'" << std::endl;
                return 1;
            }
            line = "";
            while (std::getline(errfile, line))
            {
                if (line.find("DUE TO TIME LIMIT") != std::string::npos)
                {
                    classification = TIMEOUT;
                    break;
                }
            }
            errfile.close();
        }

        // actually update outcome
        outcomes[key] = classification;
        std::cout << "\r" << ++processed_count << std::flush;
    }

    // collect outputs
    std::map<int, std::set<std::pair<int, int>>> outcome_sets;
    outcome_sets[EMPTY];
    outcome_sets[INVERTED_INPUT];
    outcome_sets[SPLIT_FAILED];
    outcome_sets[TIMEOUT];
    outcome_sets[COMPLETED];
    outcome_sets[OTHER];
    for (const auto pair : outcomes)
    {
        auto key = pair.first;
        int outcome = pair.second;
        outcome_sets[outcome].insert(key);
    }

    // print findings
    std::cout << "====== FINDINGS ======" << std::endl;
    std::cout << "total runs (sanity check): " << outcome_sets[EMPTY].size() + outcome_sets[INVERTED_INPUT].size() + outcome_sets[SPLIT_FAILED].size() + outcome_sets[TIMEOUT].size() + outcome_sets[COMPLETED].size() + outcome_sets[OTHER].size() << std::endl;
    std::cout << "# successes: " << outcome_sets[COMPLETED].size() << std::endl;
    std::cout << "# empty inputs: " << outcome_sets[EMPTY].size();
    for (const auto &pair : outcome_sets[EMPTY])
    {
        std::cout << "\t" << pair.first << " " << pair.second << "body" << std::endl;
    }
    std::cout << "# inverted inputs: " << outcome_sets[INVERTED_INPUT].size();
    for (const auto &pair : outcome_sets[INVERTED_INPUT])
    {
        std::cout << "\t" << pair.first << " " << pair.second << "body" << std::endl;
    }
    std::cout << "# failed splits: " << outcome_sets[SPLIT_FAILED].size();
    for (const auto &pair : outcome_sets[SPLIT_FAILED])
    {
        std::cout << "\t" << pair.first << " " << pair.second << "body" << std::endl;
    }
    std::cout << "# timeouts: " << outcome_sets[TIMEOUT].size();
    for (const auto &pair : outcome_sets[TIMEOUT])
    {
        std::cout << "\t" << pair.first << " " << pair.second << "body" << std::endl;
    }
    std::cout << "other result (debugging): " << outcome_sets[OTHER].size();
    for (const auto &pair : outcome_sets[OTHER])
    {
        std::cout << "\t" << pair.first << " " << pair.second << "body" << std::endl;
    }
}