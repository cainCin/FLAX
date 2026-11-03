# Deploy with docker on Linux:
docker run --gpus all \
	--name my_vllm_container \
	-v ~/.cache/huggingface:/root/.cache/huggingface \
 	--env "HUGGING_FACE_HUB_TOKEN=${HUGGING_FACE_HUB_TOKEN}" \
	-p 8000:8000 \
	--ipc=host \
	vllm/vllm-openai:latest \
	--model ds4sd/SmolDocling-256M-preview