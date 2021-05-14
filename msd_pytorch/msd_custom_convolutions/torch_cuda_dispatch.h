#pragma once


torch::Tensor conv_cuda_forward(torch::Tensor input_t,
				torch::Tensor kernel_t,
				torch::Tensor bias_t,
				torch::Tensor out_t,
				int dilation,
				int block_size);

void conv_cuda_backward_x(torch::Tensor grad_output_t,
                          torch::Tensor kernel_t,
                          torch::Tensor grad_input_t,
                          int dilation,
                          int block_size);

void conv_cuda_backward_k(torch::Tensor grad_output,
			  torch::Tensor input,
                          torch::Tensor grad_kernel,
                          int dilation,
			  int block_size);

torch::Tensor conv_relu_cuda_forward(torch::Tensor input_t,
				     torch::Tensor kernel_t,
				     torch::Tensor bias_t,
				     torch::Tensor out_t,
				     int dilation,
				     int block_size);

void conv_relu_cuda_backward_x(torch::Tensor output_t,
                               torch::Tensor grad_output_t,
                               torch::Tensor kernel_t,
                               torch::Tensor grad_input_t,
                               int dilation,
                               int block_size);

void conv_relu_cuda_backward_k(torch::Tensor output,
			       torch::Tensor grad_output,
			       torch::Tensor input,
                               torch::Tensor grad_kernel,
                               int dilation,
			       int block_size);

void conv_relu_cuda_backward_bias(torch::Tensor output,
                                  torch::Tensor grad_output,
                                  torch::Tensor grad_bias,
                                  int block_size);

// 3D functions
torch::Tensor conv3d_cuda_forward(torch::Tensor input_t,
                                  torch::Tensor kernel_t,
                                  torch::Tensor bias_t,
                                  torch::Tensor out_t,
                                  int dilation,
                                  int block_size);

torch::Tensor conv3d_relu_cuda_forward(torch::Tensor input_t,
                                       torch::Tensor kernel_t,
                                       torch::Tensor bias_t,
                                       torch::Tensor out_t,
                                       int dilation,
                                       int block_size);

void conv3d_cuda_backward_x(torch::Tensor grad_output_t,
			    torch::Tensor kernel_t,
			    torch::Tensor grad_input_t,
			    int dilation,
			    int block_size);

void conv3d_relu_cuda_backward_x(torch::Tensor output_t,
                                 torch::Tensor grad_output_t,
                                 torch::Tensor kernel_t,
                                 torch::Tensor grad_input_t,
                                 int dilation,
                                 int block_size);

void conv3d_cuda_backward_k(torch::Tensor grad_output,
			    torch::Tensor input,
			    torch::Tensor grad_kernel,
			    int dilation,
			    int block_size);

void conv3d_relu_cuda_backward_k(torch::Tensor output,
				 torch::Tensor grad_output,
				 torch::Tensor input,
				 torch::Tensor grad_kernel,
				 int dilation,
				 int block_size);

void conv3d_relu_cuda_backward_bias(torch::Tensor output,
				    torch::Tensor grad_output,
				    torch::Tensor grad_bias,
				    int block_size);
