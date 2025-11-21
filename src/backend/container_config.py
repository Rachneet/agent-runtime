from pydantic import BaseModel, Field


class ContainerConfig(BaseModel):
    # CPU LIMITS
    # A full CPU core = 100000 microseconds per period.
    cpu_quota: int = Field(50000) # 0.5 core

    # Time window for CPU quota enforcement.
    # Default: 100000 microseconds = 100 ms
    cpu_period: int = Field(100000)

    # Relative CPU priority (only matters under CPU contention).
    cpu_shares: int = Field(512)

    # MEMORY LIMITS
    # The hard memory cap.
    # If the container exceeds this, it is OOM-killed.
    memory_limit: str = Field("512m")
    memory_swap: str = Field("512m")

    # A soft limit.
    memory_reservation: str = Field("256m")

    # STORAGE LIMITS
    # Not a Docker feature, the application checks file size before running
    storage_limit_mb: int = Field(100)

    # EXECUTION LIMITS
    # The app kills the container after X seconds.
    execution_timeout: int = Field(300)

    # NETWORK
    # When disabled:
    # ✔ no outgoing internet
    # ✔ no DNS
    # ✔ no TCP/UDP
    # ✔ no ping
    # Makes the container sandboxed & secure.
    enable_network: bool = Field(True)

    # PROCESS LIMITS
    # Maximum number of OS processes + threads the container can create.
    pids_limit: int = Field(100)

    # FILESYSTEM SECURITY
    # If True:
    # ✔ filesystem cannot be modified
    # ✔ /tmp is the only writable directory (via tmpfs you set)
    # ✔ protects from malware writing files
    read_only_root: bool = Field(True)
    tmpfs_size: str = Field("100m")

    # SECURITY
    # Dropping all means:
    # ✔ cannot bind to low ports
    # ✔ cannot modify network settings
    # ✔ cannot mount filesystems
    # ✔ cannot change owner or permissions
    # ✔ cannot load kernel modules
    drop_all_capabilities: bool = Field(True)
    no_new_privileges: bool = Field(True)

    # RATE LIMITING
    # your system limit.
    max_jobs_per_minute: int = Field(10)

    # LOGGING
    log_level: str = Field("INFO")
    log_resource_usage: bool = Field(True)
