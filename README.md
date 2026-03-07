# doc-store-server

## TODO

- [ ] use seperate credentials for deploy and terraform

## Local development

podman build -t doc-store .

podman run -it --rm --name doc-store -v ./app:/app:z -p 8080:8080 doc-store