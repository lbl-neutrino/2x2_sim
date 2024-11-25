#include <iostream>
#include <fstream>

#include "TMath.h"
#include "TTree.h"
#include "TFile.h"
#include "TRandom.h"
#include "TDatabasePDG.h"
#include "TObjString.h"

#define CM2M 0.01

using namespace std;

enum class Format { UNDEFINED, NORMAL, COMPACT };
static constexpr unsigned _fbsize_words = 5733 + 2;
static constexpr float box_width[3] = {0.31039 * 2, 1.24078, 0.3151745 * 2}; // meters
static constexpr float x_border[2] = {-3.10390000e-01,  3.10390000e-01};
static constexpr float y_border[2] = {-8.38626000e-01,  4.02154000e-01};
static constexpr float z_border[2] = {-3.15174500e-01,  3.15174500e-01};

static constexpr float ceiling = 10; // where we start the simulation in y

union {
	float fl[_fbsize_words];
	unsigned in[_fbsize_words];
	char ch[sizeof(fl[0])*_fbsize_words];
} buf;

const std::map<unsigned int, int> corsikaToPdgId = {
	{1, 22},     // gamma
	{2, -11},    // e+
	{3, 11},     // e-
	{5, -13},    // mu+
	{6, 13},     // mu-
	{7, 111},    // pi0
	{8, 211},    // pi+
	{9, -211},   // pi-
	{10, 130},   // K0_L
	{11, 321},   // K+
	{12, -321},  // K-
	{13, 2112},  // n
	{14, 2212},  // p
	{15, -2212}, // pbar
	{16, 310},   // K0_S
	{17, 221},   // eta
	{18, 3122},  // Lambda
	{19, 3222},  // Sigma+
	{20, 3212},  // Sigma0
	{21, 3112},  // Sigma-
	{22, 3322},  // Cascade0
	{23, 3312},  // Cascade-
	{24, 3334},  // Omega-
	{25, -2112}, // nbar
	{26, -3122}, // Lambdabar
	{27, -3112}, // Sigma-bar
	{28, -3212}, // Sigma0bar
	{29, -3222}, // Sigma+bar
	{30, -3322}, // Cascade0bar
	{31, -3312}, // Cascade+bar
	{32, -3334}, // Omega+bar

	{50, 223},    // omega
	{51, 113},    // rho0
	{52, 213},    // rho+
	{53, -213},   // rho-
	{54, 2224},   // Delta++
	{55, 2214},   // Delta+
	{56, 2114},   // Delta0
	{57, 1114},   // Delta-
	{58, -2224},  // Delta--bar
	{59, -2214},  // Delta-bar
	{60, -2114},  // Delta0bar
	{61, -1114},  // Delta+bar
	{62, 10311},  // K*0
	{63, 10321},  // K*+
	{64, -10321}, // K*-
	{65, -10311}, // K*0bar
	{66, 12},     // nu_e
	{67, -12},    // nu_ebar
	{68, 14},     // nu_mu
	{69, -14},    // nu_mubar

	{116, 421},  // D0
	{117, 411},  // D+
	{118, -411}, // D-bar
	{119, -421}, // D0bar
	{120, 431},  // D+_s
	{121, -431}, // D-_sbar
	{122, 441},  // eta_c
	{123, 423},  // D*0
	{124, 413},  // D*+
	{125, -413}, // D*-bar
	{126, -423}, // D*0bar
	{127, 433},  // D*+_s
	{128, -433}, // D*-_s

	{130, 443}, // J/Psi
	{131, -15}, // tau+
	{132, 15},  // tau-
	{133, 16},  // nu_tau
	{134, -16}, // nu_taubar

	{137, 4122},  // Lambda+_c
	{138, 4232},  // Cascade+_c
	{139, 4132},  // Cascade0_c
	{140, 4222},  // Sigma++_c
	{141, 4212},  // Sigma+_c
	{142, 4112},  // Sigma0_c
	{143, 4322},  // Cascade'+_c
	{144, 4312},  // Cascade'0_c
	{145, 4332},  // Omega0_c
	{149, -4122}, // Lambda-_cbar
	{150, -4232}, // Cascade-_cbar
	{151, -4132}, // Cascade0_cbar
	{152, -4222}, // Sigma--_cbar
	{153, -4212}, // Sigma-_cbar
	{154, -4112}, // Sigma0_cbar
	{155, -4322}, // Cascade'-_cbar
	{156, -4312}, // Cascade'0_cbar
	{157, -4332}, // Omega0_cbar
	{161, 4224},  // Sigma*++_c
	{162, 1214},  // Sigma*+_c
	{163, 4114},  // Sigma*0_c

	{171, -4224},     // Sigma*--_cbar
	{172, -1214},     // Sigma*-_cbar
	{173, -4114},     // Sigma*0_cbar
	{176, 511},       // B0
	{177, 521},       // B+
	{178, -521},      // B-bar
	{179, -511},      // B0bar
	{180, 531},       // B0_s
	{181, -531},      // B0_sbar
	{182, 541},       // B+_c
	{183, -541},      // B-_cbar
	{184, 5122},      // Lambda0_b
	{185, 5112},      // Sigma-_b
	{186, 5222},      // Sigma+_b
	{187, 5232},      // Cascade0_b
	{188, 5132},      // Cascade-_b
	{189, 5332},      // Omega-_b
	{190, -5112},     // Lambda0_bbar
	{191, -5222},     // Sigma+_bbar
	{192, -5112},     // Sigma-_bbar
	{193, -5232},     // Cascade0_bbar
	{194, -5132},     // Cascade+_bbar
	{195, -5332},      // Omega+_bbar

	{201, 1000010020}, // Deuteron
	{301, 1000010030}, // Tritium
	{402, 1000020040}, // alpha
	{5626, 1000260560}, // Iron
	{1206, 1000080120}, // Carbon
	{1407, 1000070140}, // Nitrogen
	{1608, 1000080160}, // Oxygen
	{2713, 1000130270}, // Aluminum
	{3216, 1000160320}, // Sulfur
	{2814, 1000140280}, // Silicon
	{9900, 22}          // Cherenkov gamma
};

int main(int argc, char *argv[]) {
	if (argc == 1) {
		std::cout << "Usage: corsikaConverter INPUT" << std::endl;
		return 0;
	}

	ifstream *input = new ifstream(argv[1]);;
    int current_event_number = -1;
    int event_count = 0;
    int run_number = -1;
    Format _infmt = Format::UNDEFINED;

	TDatabasePDG *pdg_database = TDatabasePDG::Instance();
	pdg_database->ReadPDGTable();

	char outputFilename[256];
	strcpy(outputFilename, argv[1]);
	strcat(outputFilename,".root");

	TFile *gRooTrackerFile = new TFile(outputFilename,"RECREATE");
	TTree *gRooTracker = new TTree("gRooTracker", "gRooTracker");
	static constexpr unsigned kMaxParticles = 39;
	TRandom *xyzRandom = new TRandom();
	//TRandom *particleIndex = new TRandom();

	Int_t EvtNum;
	TBits *EvtFlags = new TBits();
	TObjString *EvtCode = new TObjString("");
	Double_t EvtVtx [4];
	Double_t EvtXSec = 1.;
	Double_t EvtDXSec = 1.;
	Double_t EvtWght = 1.;
	Double_t EvtProb = 1.;
	Int_t StdHepPdg[kMaxParticles];
	Int_t StdHepN;
	Int_t StdHepStatus[kMaxParticles];
	Int_t StdHepRescat[kMaxParticles];
	Double_t StdHepP4[kMaxParticles][4];
	Double_t StdHepX4[kMaxParticles][4];
	Double_t StdHepPolz[kMaxParticles][3];
	Int_t StdHepFd[kMaxParticles];
	Int_t StdHepLd[kMaxParticles];
	Int_t StdHepFm[kMaxParticles];
	Int_t StdHepLm[kMaxParticles];
	Int_t NuParentPdg;
	Int_t NuParentDecMode;
	Double_t NuParentDecP4[4];
	Double_t NuParentDecX4[4];
	Double_t NuParentProX4[4];
	Double_t NuParentProP4[4];
	Int_t NuParentProNVtx;
	gRooTracker->Branch("EvtNum", &EvtNum, "EvtNum/I");
    gRooTracker->Branch("EvtFlags", "TBits", &EvtFlags, 32000, 1);
    gRooTracker->Branch("EvtCode", "TObjString", &EvtCode, 32000, 1);
	gRooTracker->Branch("EvtVtx", EvtVtx, "EvtVtx[4]/D");
	gRooTracker->Branch("EvtXSec", &EvtXSec, "EvtXsec/D");
	gRooTracker->Branch("EvtDXSec", &EvtDXSec, "EvtDXsec/D");
	gRooTracker->Branch("EvtWght", &EvtWght, "EvtWght/D");
	gRooTracker->Branch("EvtProb", &EvtProb, "EvtProb/D");
	gRooTracker->Branch("StdHepN", &StdHepN, "StdHepN/I");
	gRooTracker->Branch("StdHepPdg", StdHepPdg, "StdHepPdg[StdHepN]/I");
	gRooTracker->Branch("StdHepStatus", StdHepStatus, "StdHepStatus[StdHepN]/I");
	gRooTracker->Branch("StdHepRescat", StdHepRescat, "StdHepRescat[StdHepN]/I");
	gRooTracker->Branch("StdHepP4", StdHepP4, "StdHepP4[StdHepN][4]/D");
	gRooTracker->Branch("StdHepX4", StdHepX4, "StdHepX4[StdHepN][4]/D");
	gRooTracker->Branch("StdHepPolz", StdHepPolz, "StdHepPolz[StdHepN][3]/D");
	gRooTracker->Branch("StdHepFd", StdHepFd, "StdHepFd[StdHepN]/I");
	gRooTracker->Branch("StdHepLd", StdHepLd, "StdHepLd[StdHepN]/I");
	gRooTracker->Branch("StdHepFm", StdHepFm, "StdHepFm[StdHepN]/I");
	gRooTracker->Branch("StdHepLm", StdHepLm, "StdHepLm[StdHepN]/I");

	gRooTracker->Branch("NuParentPdg", &NuParentPdg, "NuParentPdg/I");
	gRooTracker->Branch("NuParentDecMode", &NuParentDecMode, "NuParentDecMode/I");
	gRooTracker->Branch("NuParentDecP4", NuParentDecP4, "NuParentDecP4[4]/D");
	gRooTracker->Branch("NuParentDecX4", NuParentDecX4, "NuParentDecX4[4]/D");
	gRooTracker->Branch("NuParentProP4", NuParentProP4, "NuParentProP4[4]/D");
	gRooTracker->Branch("NuParentProX4", NuParentProX4, "NuParentProX4[4]/D");
	gRooTracker->Branch("NuParentProNVtx", &NuParentProNVtx, "NuParentProNVtx/I");

    while( input->read(buf.ch, 4)) {
      unsigned reclen = buf.in[0];
      // CORSIKA records are in units of 4 bytes
      if(reclen % 4) {
        throw std::runtime_error("Error: record size not a multiple of 4");
      }

      // We will be looking at at least 8 bytes to determine the
      // input file format, and all real CORSIKA records are longer
      // than that.
      if(reclen < 2*4) {
        throw std::runtime_error("Error: reclen too small");
      }

      // Read the full record
      if(!input->read(buf.ch, reclen)) {
        break;
      }

      // Determine the format and and store the decision for future blocks.
      // We are starting file read, so should see the RUNH marker
      // In COMPACT format each block is preceded by 4 bytes
      // giving the size of the block in words.

      if(!strncmp(buf.ch+0, "RUNH", 4)) {
        std::cout<<"Reading NORMAL format"<<std::endl;
        _infmt = Format::NORMAL;
      }
      else if(!strncmp(buf.ch+4, "RUNH", 4)) {
        std::cout<<"Reading COMPACT format"<<std::endl;
        _infmt = Format::COMPACT;
      }
      else {
        throw std::runtime_error("Error: did not find the RUNH record to determine COMPACT flag");
      }

      unsigned iword = 0;
      if(_infmt == Format::COMPACT) {
        // Move to the beginning of the actual block
        ++iword;
      }

      break;

    }

	input->clear();
    input->seekg(0, ios::beg);
    unsigned particleCounter = 0;
	// bool eventWithParticle = false;
	// FORTRAN sequential records are prefixed with their length
	// in a 4-byte word
	while( input->read(buf.ch, 4)) {

		unsigned reclen = buf.in[0];
		// CORSIKA records are in units of 4 bytes
		if(reclen % 4) {
			throw std::runtime_error("Error: record size not a multiple of 4");
		}

		// We will be looking at at least 8 bytes to determine the
		// input file format, and all real CORSIKA records are longer
		// than that.
		if(reclen < 2*4) {
			throw std::runtime_error("Error: reclen too small");
		}

		if(reclen > 4*_fbsize_words) {
			throw std::runtime_error("Error: reclen too big");
		}

		// Read the full record
		if(!input->read(buf.ch, reclen)) {
			break;
		}

		//================================================================
		// Go over blocks in the record
		for(unsigned iword = 0; iword < reclen/4; ) {

			unsigned block_words = (_infmt == Format::COMPACT) ? buf.in[iword] : 273;

			if(!block_words) {
				throw std::runtime_error("Got block_words = 0\n");
			}

			if(_infmt == Format::COMPACT) {
				// Move to the beginning of the actual block
				++iword;
			}

			std::string event_marker = (_infmt == Format::NORMAL || !event_count) ? "EVTH" : "EVHW";

			// Determine the type of the data block
			if(!strncmp(buf.ch+4*iword, "RUNH", 4)) {
				run_number = lrint(buf.fl[1+iword]);
				float lowE = float(buf.fl[16+iword]);
				float highE = float(buf.fl[17+iword]);
				std::cout << "Start Run " << run_number << std::endl;
				std::cout << "Primary proton energy between " << lowE << " and " << highE << std::endl;
			}
			else if (!strncmp(buf.ch+4*iword, "RUNE", 4)) {
				int end_run_number = lrint(buf.fl[1+iword]);
				int end_event_count = lrint(buf.fl[2+iword]);
				std::cout << "End Run " << run_number << std::endl;

				if(end_run_number != run_number) {
					throw std::runtime_error("Error: run number mismatch in end of run record\n");
				}

				if(event_count != end_event_count) {
					std::cerr<<"RUNE: _event_count = "<<event_count<<" end record = "<<end_event_count<<std::endl;
					throw std::runtime_error("Error: event count mismatch in end of run record\n");
				}

				gRooTracker->Write();
				gRooTrackerFile->Close();

				// Exit the read loop at the end of run
				return 0;
			}
			else if(!strncmp(buf.ch+4*iword, event_marker.data(), 4)) {

				current_event_number = lrint(buf.fl[1+iword]);

				// if (eventWithParticle) {
				// 	// Clear arrays
				// 	memset(StdHepPdg, 0, sizeof(StdHepPdg));
				// 	memset(StdHepP4, 0, sizeof(StdHepP4));
				// 	memset(StdHepX4, 0, sizeof(StdHepX4));
				// 	memset(StdHepStatus, 0, sizeof(StdHepStatus));
				// 	memset(EvtVtx, 0, sizeof(EvtVtx));
				// 	StdHepN = 0;
				// 	StdHepStatus[StdHepN] = -1;
				// 	EvtNum = particleCounter;
				// 	StdHepN++;
				// 	gRooTracker->Fill();
				// 	particleCounter++;
				// }

				// eventWithParticle = false;
				++event_count;
			}
			else if(!strncmp(buf.ch+4*iword, "EVTE", 4)) {
				int end_event_number = lrint(buf.fl[1+iword]);
				if(end_event_number != current_event_number) {
					throw std::runtime_error("Error: event number mismatch in end of event record\n");
				}
			}
			else {
				// const float x_shift = zxRandom->Uniform(-box_width[0]/2,box_width[0]/2);
				// const float z_shift = zxRandom->Uniform(-box_width[0]/2,box_width[0]/2);
				std::vector<float> x;
				std::vector<float> z;
				std::vector<float> px;
				std::vector<float> py;
				std::vector<float> pz;
				std::vector<int> pdg;
				for (unsigned i_part = 0; i_part < block_words; i_part+=7) {
					unsigned id = buf.fl[iword + i_part] / 1000;
					if (id == 0)
						continue;
					x.push_back(buf.fl[iword + i_part + 4] * CM2M);
					z.push_back(buf.fl[iword + i_part + 5] * CM2M);
					px.push_back(buf.fl[iword + i_part + 1]);
					pz.push_back(buf.fl[iword + i_part + 2]);
					py.push_back(-buf.fl[iword + i_part + 3]);
					pdg.push_back(corsikaToPdgId.at(id));
				}

				//const unsigned pidx = particleIndex->Integer(x.size());
				//const float momentum = sqrt(px[pidx]*px[pidx] + py[pidx]*py[pidx] + pz[pidx]*pz[pidx]);
				//const std::vector<float> dir_vector{ px[pidx]/momentum, py[pidx]/momentum, pz[pidx]/momentum };
				//const float random_y = xyzRandom->Uniform(y_border[0],y_border[1]);
				//const float t = (random_y-ceiling)/dir_vector[1];
				//const float x_particle = x[pidx] + dir_vector[0]*t;
				//const float z_particle = z[pidx] + dir_vector[2]*t;
				//const float deltax[2] = {x_particle-x_border[1],x_particle-x_border[0]};
				//const float deltaz[2] = {z_particle-z_border[1],z_particle-z_border[0]};
				//const float x_shift = xyzRandom->Uniform(*std::min_element(deltax,deltax+2), *std::max_element(deltax,deltax+2));
				//const float z_shift = xyzRandom->Uniform(*std::min_element(deltaz,deltaz+2), *std::max_element(deltaz,deltaz+2));

				for (unsigned i_part = 0; i_part < x.size(); i_part++) {
					const float momentum = sqrt(px[i_part]*px[i_part] + py[i_part]*py[i_part] + pz[i_part]*pz[i_part]);
					const std::vector<float> dir_vector{ px[i_part]/momentum, py[i_part]/momentum, pz[i_part]/momentum };
					const float random_y = xyzRandom->Uniform(y_border[0],y_border[1]);
					const float t = (random_y-ceiling)/dir_vector[1];
					const float x_particle = x[i_part] + dir_vector[0]*t;
					const float z_particle = z[i_part] + dir_vector[2]*t;
					const float deltax[2] = {x_particle-x_border[1],x_particle-x_border[0]};
					const float deltaz[2] = {z_particle-z_border[1],z_particle-z_border[0]};
					const float x_shift = xyzRandom->Uniform(*std::min_element(deltax,deltax+2), *std::max_element(deltax,deltax+2));
					const float z_shift = xyzRandom->Uniform(*std::min_element(deltaz,deltaz+2), *std::max_element(deltaz,deltaz+2));

					for (int nx = -5; nx <= 5; nx++) {
						for (int nz = -5; nz <= 5; nz++) {
							// Clear variables
							memset(StdHepPdg, 0, sizeof(StdHepPdg));
							memset(StdHepP4, 0, sizeof(StdHepP4));
							memset(StdHepX4, 0, sizeof(StdHepX4));
							memset(StdHepStatus, 0, sizeof(StdHepStatus));
							memset(EvtVtx, 0, sizeof(EvtVtx));
							StdHepN = 0;
							StdHepPdg[StdHepN] = pdg[i_part];
							StdHepStatus[StdHepN] = 1;
							StdHepP4[StdHepN][0] = px[i_part];
							StdHepP4[StdHepN][1] = py[i_part]; // Here we switch z and y because in the GDML
							StdHepP4[StdHepN][2] = pz[i_part]; // y is the vertical coordinate
							const float mass = pdg_database->GetParticle(pdg[i_part])->Mass();
							const float energy = sqrt(mass*mass + momentum*momentum);
							StdHepP4[StdHepN][3] = energy;
							StdHepX4[StdHepN][0] = 0;
							StdHepX4[StdHepN][1] = 0;
							StdHepX4[StdHepN][2] = 0;
							StdHepX4[StdHepN][3] = 0;
							EvtVtx[0] = x[i_part] - x_shift + nx*(x_border[1]-x_border[0]);
							EvtVtx[1] = ceiling;
							EvtVtx[2] = z[i_part] - z_shift + nz*(z_border[1]-z_border[0]);
							EvtNum = particleCounter;
							StdHepN++;
							gRooTracker->Fill();
							particleCounter++;
						//}

						//if (StdHepN > 0) {
							memset(StdHepPdg, 0, sizeof(StdHepPdg));
							memset(StdHepP4, 0, sizeof(StdHepP4));
							memset(StdHepX4, 0, sizeof(StdHepX4));
							memset(StdHepStatus, 0, sizeof(StdHepStatus));
							memset(EvtVtx, 0, sizeof(EvtVtx));
							StdHepN = 0;
							EvtNum = particleCounter;
							StdHepStatus[StdHepN] = -1;
							StdHepN++;
							gRooTracker->Fill();
							particleCounter++;
						}
					}

				}
			}

			// Move to the next block
			iword += block_words;

		} // loop over blocks in a record

		// Here we expect the FORTRAN end of record padding,
		// read and verify its value.
		if(!input->read(buf.ch, 4)) {
			break;
		}

		if(buf.in[0] != reclen) {
			throw std::runtime_error("Error: unexpected FORTRAN record end padding");
		}

	} // loop over records

	return 0;
}
