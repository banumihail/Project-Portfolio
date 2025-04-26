%% Plotting the original data (for reference)
figure;
mesh(id.X{1}, id.X{2}, id.Y);
title('Original Training Data');
hold on;

%% Setting the degree of polynomial approximation
m_degree = 1:20;
mse_train_all = zeros(length(m_degree), 1);  % Store training MSEs
mse_val_all = zeros(length(m_degree), 1);  % Store validation MSEs

%% Loop over degrees of polynomial m to find MSEs
for idx = 1:length(m_degree)
    m = m_degree(idx);  % Current degree

    %% Building the Regressor matrix based on the degree of m
    n1 = length(id.X{1});
    n2 = length(id.X{2});
    R = [];

    for i = 1:n1
        for j = 1:n2
            x1 = id.X{1}(i);
            x2 = id.X{2}(j);
            R = [R; polyfeatures(x1, x2, m)];  % Create Polynomial terms
        end
    end

    %% Finding Theta (o) using least squares
    Y_column = reshape(id.Y', [], 1);  % Reshape Y to a column vector
    o = R \ Y_column;  % Solve for theta

    %% Predicted Y2 for the training set
    Y2 = R * o;

    %% Finding MSE for Training Set
    mse_train = mean((Y_column - Y2).^2);
    mse_train_all(idx) = mse_train;  % Store the training MSE for the current degree

    %% Now the same for the validation set
    n1_val = length(val.X{1});
    n2_val = length(val.X{2});
    R_val = [];

    for i = 1:n1_val
        for j = 1:n2_val
            x1_val = val.X{1}(i);
            x2_val = val.X{2}(j);
            R_val = [R_val; polyfeatures(x1_val, x2_val, m)];
        end
    end

    Y_val_column = reshape(val.Y', [], 1);  % Reshape validation Y into a column vector
    Y2_val = R_val * o;  % Predict for the validation set

    %% Finding MSE for Validation Set
    mse_val = mean((Y_val_column - Y2_val).^2);
    mse_val_all(idx) = mse_val;  % Store the validation MSE for the current degree
end

%% Find the best degree m with the smallest difference between training and validation MSE
[~, best_m_idx] = min(abs(mse_train_all - mse_val_all));  % Index of the smallest MSE difference
best_m = m_degree(best_m_idx);  % Corresponding best polynomial degree

disp(['Best polynomial degree (m): ', num2str(best_m)]);

%% Now only plot the surface for the best degree m

% Recalculate the Regressor matrix for the best degree m
R_best = [];
for i = 1:n1
    for j = 1:n2
        x1 = id.X{1}(i);
        x2 = id.X{2}(j);
        R_best = [R_best; polyfeatures(x1, x2, best_m)];
    end
end

% Solve for theta again using the best degree
o_best = R_best \ reshape(id.Y', [], 1);

% Recalculate the regressor matrix for the validation set
R_best_val = [];
for i = 1:n1_val
    for j = 1:n2_val
        x1_val = val.X{1}(i);
        x2_val = val.X{2}(j);
        R_best_val = [R_best_val; polyfeatures(x1_val, x2_val, best_m)];
    end
end

% Predict Y2 for the validation set using the best degree
Y2_val_best = R_best_val * o_best;

% Plot the surface for the best degree m
figure;
surf(reshape(val.X{1}, n1_val, []), reshape(val.X{2}, n2_val, []), reshape(Y2_val_best, n1_val, []));
title(['Validation Set Prediction with Best Polynomial Degree m = ', num2str(best_m)]);
xlabel('X1');
ylabel('X2');
zlabel('Predicted Y (Validation)');
grid on;

%% Compare MSE values for different degrees m
figure;
plot(m_degree, mse_train_all, '-o', 'DisplayName', 'Training MSE');
hold on;
plot(m_degree, mse_val_all, '-o', 'DisplayName', 'Validation MSE');
title('MSE for Different Polynomial Degrees (m)');
xlabel('Polynomial Degree (m)');
ylabel('Mean Squared Error (MSE)');
legend;
grid on;


%% Function for generating polynomial features up to degree m
function Phi = polyfeatures(x1, x2, m)
    % Generates polynomial features of x1, x2 up to degree m
    % Example: for m=2, we return [1, x1, x2, x1^2, x2^2, x1*x2]
    
    Phi = 1;  % Start with the bias term
    for i = 1:m
        for j = 0:i
            Phi = [Phi, (x1^(i-j)) * (x2^j)];  % Polynomial terms with interactions
        end
    end
end
