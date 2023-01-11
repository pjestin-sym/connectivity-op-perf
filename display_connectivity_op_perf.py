from datetime import datetime, timedelta
import json
import matplotlib.pyplot as plt
import subprocess

SPAN: timedelta = timedelta(hours=1)

def get_install_timestamp(sym_connectivity) -> datetime | None:
  for condition in sym_connectivity['status']['conditions']:
    if 'reason' in condition and condition['reason'] == 'InstallSuccessful':
      return datetime.strptime(condition['lastTransitionTime'], '%Y-%m-%dT%H:%M:%SZ')
  return None

def get_timestamp_data() -> list[tuple[datetime, timedelta]]:
  sym_connectivites = json.loads(subprocess.run(["kubectl get symconnectivity -A -o json"], shell=True, stdout=subprocess.PIPE).stdout.decode("utf-8"))

  timestamps: list[tuple[datetime, timedelta]] = []

  for sym_connectivity in sym_connectivites['items']:
    creation_timestamp: datetime = datetime.strptime(sym_connectivity['metadata']['creationTimestamp'], '%Y-%m-%dT%H:%M:%SZ')
    install_timestamp: datetime | None = get_install_timestamp(sym_connectivity)
    if install_timestamp:
      timestamps.append((creation_timestamp, install_timestamp - creation_timestamp))

  return sorted(timestamps, key=lambda timestamp: timestamp[0])

def display_chart(timestamps: list[tuple[datetime, timedelta]])-> None:
  x: list[datetime] = []
  y: list[float] = []

  min_creation_timestamp: datetime = timestamps[0][0]
  max_creation_timestamp: datetime = timestamps[-1][0]

  creation_timestamp: datetime = min_creation_timestamp
  timestamp_index: int = 0
  while creation_timestamp < max_creation_timestamp:
    max_duration_over_period: timedelta = timedelta(seconds=0)
    #duration_sum: timedelta = timedelta(seconds=0)
    #duration_count: int = 0
    while timestamp_index < len(timestamps) and timestamps[timestamp_index][0] < creation_timestamp + SPAN:
      #duration_sum += timestamps[timestamp_index][1]
      #duration_count += 1
      if timestamps[timestamp_index][1] and timestamps[timestamp_index][1] > max_duration_over_period:
        max_duration_over_period = timestamps[timestamp_index][1]
      timestamp_index += 1
    if max_duration_over_period.seconds > 0:
      x.append(creation_timestamp)
      #y.append((duration_sum / duration_count).seconds)
      y.append(max_duration_over_period.seconds)
    creation_timestamp += SPAN

  plt.plot(x, y)

  plt.xlabel('Creation time')
  plt.ylabel('Maximum installation duration (s)')

  plt.title('Connectivity operator performance')
  plt.show()

def main():
  timestamps: list[tuple[datetime, timedelta]] = get_timestamp_data()
  display_chart(timestamps)

if __name__ == '__main__':
  main()
