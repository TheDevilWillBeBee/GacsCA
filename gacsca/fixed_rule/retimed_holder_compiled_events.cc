// Execution acceleration only: every literal event calls the unchanged full F.
// This scheduler has no hierarchy/depth input and retains every procedure word.
#include <algorithm>
#include <array>
#include <cstdint>
#include <cstring>
#include <vector>
#include "events_config.h"

extern "C" void retimed_holder_local(const uint64_t*, uint64_t*);
using Row = std::array<uint64_t, PROCS>;
struct Plan { uint64_t distance; int velocity; bool waiting; };

static Plan plan(const uint64_t* row, uint64_t address, const uint64_t* rom) {
    if (row[DIRECTION]) return {address, -1, false};
    const uint64_t* meta = rom + address*7;
    if (row[PHASE] == FETCH && meta[0] == WAIT && meta[1] == row[PC] && row[RD])
        return {row[RD], 0, true};
    uint64_t target = ROM_ROWS-1, candidate = UINT64_MAX;
    if (row[PHASE] == FETCH && row[PC] < ROM_ROWS-MEM_ROWS-1)
        candidate = MEM_ROWS+row[PC];
    else if ((row[PHASE] == READ_A || row[PHASE] == TRANSMIT || row[PHASE] == READ_LOAD) && row[RA] < MEM_ROWS)
        candidate = row[RA];
    else if (row[PHASE] == READ_B && row[RB] < MEM_ROWS) candidate = row[RB];
    else if (row[PHASE] == WRITE && row[RD] < MEM_ROWS) candidate = row[RD];
    else if (row[PHASE] == READ_META && row[VALUE] && row[RD] < ROM_ROWS) candidate = row[RD];
    if (address <= candidate && candidate < target) target = candidate;
    return {target-address, 1, false};
}

// stats: elapsed, literal ticks, transport ticks, local evaluations, trace count,
// final head count. Trace entries are kind / absolute time / duration.
extern "C" int ce_run(uint64_t* words, const uint64_t* signals,
                      const uint64_t* base, const uint64_t* rom,
                      uint64_t size, uint64_t age, uint64_t absolute_time,
                      uint64_t ticks, uint64_t event_budget,
                      uint64_t* head_buffer, uint64_t head_count,
                      uint64_t* trace, uint64_t capacity, uint64_t* stats) {
    std::fill(stats, stats+6, 0);
    std::vector<uint64_t> heads(head_buffer, head_buffer+head_count);
    int result = 0;
    uint64_t input[15*FIELDS], output[FIELDS];
    while (stats[0] < ticks && stats[4] < capacity) {
        std::vector<Plan> plans;
        uint64_t amount = ticks-stats[0];
        for (uint64_t pos : heads) {
            plans.push_back(plan(words+pos*PROCS, pos%Q, rom));
            amount = std::min(amount, plans.back().distance);
        }
        for (size_t i=0; i<heads.size(); ++i) for (size_t j=i+1; j<heads.size(); ++j)
            if (plans[i].velocity != plans[j].velocity) {
                const uint64_t gap = heads[j]-heads[i];
                amount = std::min(amount, gap > 2 ? (gap-2)/2 : uint64_t(0));
            }
        const uint64_t before = absolute_time+stats[0];
        if (amount) {
            std::vector<Row> old(heads.size());
            for (size_t i=0; i<heads.size(); ++i) {
                std::copy(words+heads[i]*PROCS, words+(heads[i]+1)*PROCS, old[i].begin());
                for (unsigned k : CONTROL) words[heads[i]*PROCS+k] = 0;
            }
            for (size_t i=0; i<heads.size(); ++i) {
                if (plans[i].velocity < 0) heads[i] -= amount;
                if (plans[i].velocity > 0) heads[i] += amount;
                if (plans[i].waiting) old[i][RD] -= amount;
                for (unsigned k : CONTROL) words[heads[i]*PROCS+k] = old[i][k];
            }
            std::sort(heads.begin(), heads.end());
            stats[0] += amount; stats[2] += amount;
            trace[3*stats[4]] = 0; trace[3*stats[4]+1] = before;
            trace[3*stats[4]+2] = amount; ++stats[4];
            continue;
        }
        if (stats[1] >= event_budget) { result = 1; break; }
        std::vector<uint64_t> candidates;
        for (uint64_t pos : heads) for (int d=-1; d<=1; ++d)
            candidates.push_back((pos+size+d)%size);
        std::sort(candidates.begin(), candidates.end());
        candidates.erase(std::unique(candidates.begin(), candidates.end()), candidates.end());
        std::vector<Row> updates(candidates.size());
        std::vector<uint64_t> next_heads;
        for (size_t index=0; index<candidates.size(); ++index) {
            const uint64_t center = candidates[index];
            for (int j=-7; j<=7; ++j) {
                const uint64_t pos = (center+size+j)%size;
                uint64_t* cell = input+(j+7)*FIELDS;
                std::memcpy(cell, base+(pos%Q)*FIELDS, FIELDS*sizeof(uint64_t));
                cell[RAW_AGE] = age+stats[0]; cell[RAW_SIGNAL] = signals[pos];
                for (int d=-2; d<=2; ++d) {
                    const uint64_t* procedure = words+((pos+size+d)%size)*PROCS;
                    for (unsigned k=0; k<PROCS; ++k) cell[RAW_PROC[d+2][k]] = procedure[k];
                }
            }
            retimed_holder_local(input, output); ++stats[3];
            if (output[RAW_ADDRESS] != center%Q || output[RAW_AGE] != age+stats[0]+1) result = 2;
            for (unsigned k : RAW_FLAGS) if (output[k]) result = 2;
            Row& row = updates[index];
            for (unsigned k=0; k<PROCS; ++k) row[k] = output[RAW_PROC[2][k]];
            for (unsigned k : MAIL) if (row[k]) result = 2;
            if (row[HEAD]) {
                if (center%Q >= ROM_ROWS) result = 2;
                next_heads.push_back(center);
            } else for (unsigned k : CONTROL) if (row[k]) result = 2;
        }
        if (next_heads.size() > 32*(size/Q)) result = 2;
        // Domain failure leaves this simultaneous tick uncommitted.
        if (result) break;
        for (size_t i=0; i<candidates.size(); ++i)
            std::copy(updates[i].begin(), updates[i].end(), words+candidates[i]*PROCS);
        heads.swap(next_heads);
        ++stats[0]; ++stats[1];
        trace[3*stats[4]] = 1; trace[3*stats[4]+1] = before;
        trace[3*stats[4]+2] = 1; ++stats[4];
    }
    stats[5] = heads.size();
    std::copy(heads.begin(), heads.end(), head_buffer);
    return result;
}
