import paramiko


class SSHSession:
    OPEN_SSH_SESSION_WITH_PARAMIKO_TEXT = "Open SSH session with Paramiko"
    CLOSE_SSH_SESSION_WITH_PARAMIKO_TEXT = "Close SSH session with Paramiko"

    def __init__(self, name, ip_address, username, password, port=22):
        self.name = name
        self.ip_address = ip_address
        self.port = port

        self.username = username
        self.password = password

        self.paramiko_ssh_client = None

        self.standard_input = None
        self.standard_output = None
        self.standard_error = None

        self.session_opened_successfully = None
        self.command_ran_successfully = None

    def __str__(self):
        return f"{self.name} ({self.ip_address})"

    def open_ssh_session(self):
        self.information_print("Opening SSH session", SSHSession.OPEN_SSH_SESSION_WITH_PARAMIKO_TEXT)

        try:
            paramiko_ssh_client = paramiko.SSHClient()
            paramiko_ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            paramiko_ssh_client.connect(self.ip_address, username=self.username, password=self.password, port=self.port)

            self.paramiko_ssh_client = paramiko_ssh_client
            self.session_opened_successfully = True
        except OSError:
            self.information_print("Session failed to open, all operations for this session be skipped", SSHSession.CLOSE_SSH_SESSION_WITH_PARAMIKO_TEXT)
            self.session_opened_successfully = False

    def close_ssh_session(self):
        if self.session_opened_successfully:
            self.information_print("Closing SSH session", SSHSession.CLOSE_SSH_SESSION_WITH_PARAMIKO_TEXT)

            if self.standard_input:
                self.standard_input.close()

            if self.standard_output:
                self.standard_output.close()

            if self.standard_error:
                self.standard_error.close()

            if self.paramiko_ssh_client:
                self.paramiko_ssh_client.close()

    def run_command_in_ssh_session(self, command):
        if self.session_opened_successfully:
            self.information_print("Running command", command)

            try:
                self.standard_input, self.standard_output, self.standard_error = self.paramiko_ssh_client.exec_command(command.command_to_execute)

                if command.command_user_input is not None:
                    self.standard_input.write(command.command_user_input)
                    self.standard_input.flush()

                self.command_ran_successfully = True
            except EOFError:
                self.information_print("Command failed to run", command)
                self.command_ran_successfully = False

    # def download_file(self, remote_source_file_path, local_target_file_path):
    #     sftp_client = self.paramiko_ssh_client.open_sftp()
    #     sftp_client.get(remote_source_file_path, local_target_file_path)
    #     sftp_client.close()

    def upload_file(self, local_source_file_path, remote_target_file_path):
        sftp_client = self.paramiko_ssh_client.open_sftp()
        sftp_client.put(local_source_file_path, remote_target_file_path)
        sftp_client.close()

    def print_command_output(self, command):
        if self.session_opened_successfully and self.command_ran_successfully:
            if command.command_provides_output:
                self.information_print("Displaying command output", command)

            # This is required even if the command doesn't provide output because it blocks execution of the script until the command finishes.  If this is included in the
            # if-statement above, the script will exit before the command finishes running.
            while True:
                try:
                    line = self.standard_output.readline()
                except UnicodeDecodeError:
                    # Should we output that a line was omitted?
                    continue

                if not line:
                    break

                print(line, end="")

                if command.command_provides_output:
                    captured_text = line

                    if command.prefix_to_match_on_to_capture_specific_output_line is not None and line.startswith(command.prefix_to_match_on_to_capture_specific_output_line):
                        captured_text = captured_text.replace(command.prefix_to_match_on_to_capture_specific_output_line, "")

                    if command.suffix_to_match_on_to_capture_specific_output_line is not None and line.endswith(command.suffix_to_match_on_to_capture_specific_output_line):
                        captured_text = captured_text.replace(command.suffix_to_match_on_to_capture_specific_output_line, "")

                    if captured_text != line:
                        command.specifically_captured_output_text = captured_text

    def information_print(self, searchable_text, summary, command, border_symbol="*"):
        searchable_text = f"{border_symbol} {searchable_text}"
        summary = f"{border_symbol} Summary: {summary} "
        command = f"{border_symbol} Command: {command} "
        ssh_session = f"{border_symbol} SSH Session: {self} "

        lines = [searchable_text, summary, command, ssh_session]
        longest_line_length = len(max(lines, key=len))

        searchable_text = searchable_text.ljust(longest_line_length) + border_symbol
        summary = summary.ljust(longest_line_length) + border_symbol
        command = command.ljust(longest_line_length) + border_symbol
        ssh_session = ssh_session.ljust(longest_line_length) + border_symbol

        longest_line_length += len(border_symbol)

        border_line = border_symbol * longest_line_length

        print()
        print(border_line)
        print(searchable_text)
        print(summary)
        print(command)
        print(ssh_session)
        print(border_line)
        print()
