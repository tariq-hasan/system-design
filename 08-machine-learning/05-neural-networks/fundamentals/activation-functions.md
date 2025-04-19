# Activation Functions in Neural Networks

## Overview

Activation functions determine a neuron's output based on its input. They are **critical for introducing non-linearity**, which allows neural networks to learn complex patterns beyond simple linear mappings.

Without activation functions, no matter how many layers are stacked, the network would behave like a single-layer linear model.

## Categories of Activation Functions

### Linear Activation Function

**Definition**: `f(x) = x`

**Characteristics**:
- Output is identical to the input
- No transformation or squashing

**Limitations**:
- Fails to introduce non-linearity
- Multiple layers become redundant
- Derivative is constant (1), providing no meaningful gradient dynamics during backpropagation
- Not useful for complex learning tasks

**Use case**: Occasionally in the **output layer of regression tasks**, where the target can be any real number (unbounded).

### Binary Step Function

**Definition**: `f(x) = 1 if x ≥ 0, else 0`

**Characteristics**:
- Hard thresholding
- Output is binary (0 or 1)

**Limitations**:
- Not differentiable — problematic for backpropagation
- Not suitable for multi-class or continuous tasks
- No gradient information — learning stalls

**Use case**: Historical significance (e.g., perceptron models), but obsolete in modern networks.

## Non-Linear Activation Functions

These introduce the crucial non-linearities needed for neural networks to model complex data patterns.

### Sigmoid (Logistic Function)

**Definition**: `f(x) = 1 / (1 + e^(-x))`  
**Range**: (0, 1)

**Advantages**:
- Smooth and differentiable
- Useful in **binary classification** or **multi-label problems** (one output node per label)

**Disadvantages**:
- Output not zero-centered
- **Vanishing gradient**: Gradients shrink at extreme values, slowing learning in deep networks
- Saturates quickly

### TanH (Hyperbolic Tangent)

**Definition**: `f(x) = (e^x - e^-x) / (e^x + e^-x)`  
**Range**: (-1, 1)

**Advantages**:
- Zero-centered output → better gradient flow
- Preferred over sigmoid in many cases

**Disadvantages**:
- Still suffers from **vanishing gradient**
- More computationally expensive than ReLU

**Use case**: Often in **Recurrent Neural Networks (RNNs)**.

### ReLU (Rectified Linear Unit)

**Definition**: `f(x) = max(0, x)`

**Advantages**:
- Sparse activation (many neurons output 0)
- Efficient and fast
- Avoids vanishing gradient in positive region
- Accelerates convergence

**Disadvantages**:
- **Dying ReLU problem**: Neurons stuck with output 0 for all inputs (when weights push them into the negative zone)

**Use case**: **Default choice** for hidden layers in feedforward networks.

### Leaky ReLU

**Definition**: `f(x) = x if x > 0, else αx` (where α is a small constant like 0.01)

**Advantages**:
- Allows small gradient when x < 0
- Solves dying ReLU problem

**Disadvantages**:
- Still uses fixed α, which may not be optimal for all data

### Parametric ReLU (PReLU)

**Definition**: Same as Leaky ReLU, but **α is learned** via backpropagation.

**Advantages**:
- More adaptive than Leaky ReLU
- Can fit data better

**Disadvantages**:
- Adds parameters
- More computationally expensive

### ELU (Exponential Linear Unit)

**Definition**: `f(x) = x if x ≥ 0; α(e^x - 1) if x < 0`

**Advantages**:
- Smooth curve, better for gradient-based learning
- Produces negative outputs (helps zero-centering)
- Reduces bias shift in training

**Disadvantages**:
- Computationally more expensive than ReLU

### Swish

**Definition**: `f(x) = x * sigmoid(x)`  
Developed by Google.

**Advantages**:
- Smooth, non-monotonic
- Helps with **very deep networks** (40+ layers)
- Can outperform ReLU in some modern architectures

### Maxout

**Definition**: `f(x) = max(w₁x + b₁, w₂x + b₂)`

**Advantages**:
- Generalizes ReLU and Leaky ReLU
- No saturation or dying neuron problem

**Disadvantages**:
- Doubles parameters per neuron → computationally expensive
- Risk of overfitting without regularization

### Softmax (for Output Layer)

**Definition**: `f(x_i) = e^(x_i) / Σ e^(x_j)` for all j in class set  
**Range**: (0, 1), with all outputs summing to 1.

**Use case**:
- Multi-class **single-label classification** problems
- Converts raw scores (logits) into class probabilities

## Choosing the Right Activation Function

| Use Case | Suggested Activation |
|----------|-----------------------|
| **Hidden layers (general)** | ReLU (default), Leaky ReLU, PReLU |
| **Recurrent Neural Networks (RNNs)** | Tanh (or ReLU in modern RNNs) |
| **Binary classification (output layer)** | Sigmoid |
| **Multi-class classification** | Softmax |
| **Multi-label classification** | Sigmoid (1 per label) |
| **Regression (output layer)** | Linear (identity) |
| **Very deep networks (e.g. ResNets, >40 layers)** | Swish or ELU |
| **If ReLU underperforms** | Leaky ReLU → PReLU → Maxout |
