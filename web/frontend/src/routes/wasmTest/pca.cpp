// compile with 
// emcc -lembind pca.cpp -o pca.js -s ENVIRONMENT=web -s EXPORT_ES6=1 -s MODULARIZE=1 -s EXPORT_NAME="createPCA" -std=c++17 -O3 --bind -I C:\Users\jrakusch\Downloads\eigen-3.4.0


#include <emscripten/bind.h>
#include <vector>
#include <Eigen/Dense>
#include <utility>

using namespace emscripten;
using namespace Eigen;
using std::vector;

// Helper: Convert 2D vector to Eigen matrix
MatrixXd vecToEigen(const vector<vector<double>>& data) {
    int rows = data.size();
    int cols = data[0].size();
    MatrixXd mat(rows, cols);
    for (int i = 0; i < rows; ++i)
        for (int j = 0; j < cols; ++j)
            mat(i, j) = data[i][j];
    return mat;
}

int dummy(const vector<double>& data) {
	return data.size();
}

// Convert Eigen vector to std::vector
vector<double> eigenVecToStd(const VectorXd& v) {
    return vector<double>(v.data(), v.data() + v.size());
}

// --- getPrincipalComponents ---
// Returns the top 2 principal components as std::vectors
std::pair<vector<double>, vector<double>> getPrincipalComponents(const vector<vector<double>>& inputData) {
    MatrixXd data = vecToEigen(inputData);

    // Center the data
    RowVectorXd mean = data.colwise().mean();
    MatrixXd centered = data.rowwise() - mean;

    // Covariance matrix
    MatrixXd cov = (centered.adjoint() * centered) / double(data.rows() - 1);

    // Eigen decomposition
    SelfAdjointEigenSolver<MatrixXd> eig(cov);
    VectorXd eigValues = eig.eigenvalues();
    MatrixXd eigVectors = eig.eigenvectors();

    // Get the top two eigenvectors (from the *end*, since they're sorted ascending)
    int n = eigValues.size();
    VectorXd pc1 = eigVectors.col(n - 1);
    VectorXd pc2 = eigVectors.col(n - 2);

    return { eigenVecToStd(pc1), eigenVecToStd(pc2) };
}

// --- project ---
// Projects data onto the 2D space defined by pc1 and pc2
vector<vector<double>> project(const vector<double>& pc1, const vector<double>& pc2, const vector<vector<double>>& inputData) {
    MatrixXd data = vecToEigen(inputData);
    RowVectorXd mean = data.colwise().mean();
    MatrixXd centered = data.rowwise() - mean;

    VectorXd v1 = Map<const VectorXd>(pc1.data(), pc1.size());
    VectorXd v2 = Map<const VectorXd>(pc2.data(), pc2.size());

    // Create projection matrix (d x 2)
    MatrixXd projection(pc1.size(), 2);
    projection.col(0) = v1;
    projection.col(1) = v2;

    // Project data: (n x d) * (d x 2) = (n x 2)
    MatrixXd result = centered * projection;

    // Convert result to std::vector<vector<double>>
    vector<vector<double>> output(result.rows(), vector<double>(2));
    for (int i = 0; i < result.rows(); ++i) {
        output[i][0] = result(i, 0);
        output[i][1] = result(i, 1);
    }

    return output;
}

// Bindings
EMSCRIPTEN_BINDINGS(pca_module) {
    using VecD = std::vector<double>;
    using VecVecD = std::vector<std::vector<double>>;
    using PairVecD = std::pair<VecD, VecD>;

    register_vector<double>("VectorDouble");
    register_vector<VecD>("VectorVectorDouble");

    value_array<PairVecD>("PairVectorDouble")
        .element(&PairVecD::first)
        .element(&PairVecD::second);

    function("getPrincipalComponents", &getPrincipalComponents);
    function("project", &project);
	function("dummy", &dummy);
}
