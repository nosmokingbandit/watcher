FROM mattsch/fedora-rpmfusion:latest
MAINTAINER William Brown williambroown@gmail.com
 
# Install required packages
RUN dnf install -yq git \
                    python \
                    which && \
    dnf clean all
   
# Set uid/gid (override with the '-e' flag), 1000/1000 used since it's the
# default first uid/gid on a fresh Fedora install
ENV LUID=1000 LGID=1000
 
# Create the watcher user/group
RUN groupadd -g $LGID watcher && \
    useradd -c 'watcher' -s /bin/bash -m -d /opt/watcher -g $LGID -u $LUID watcher
   
# Grab the installer, do the thing
RUN git clone -q https://github.com/nosmokingbandit/watcher.git
   
# Need a config and storage volume, expose proper port
VOLUME /config
EXPOSE 9090
 
# Run our script
ENTRYPOINT ["python", "/watcher/watcher.py"]
