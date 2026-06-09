mudar o metodo de save dos embeds:
  utilizar sistemas de hexadeximal com alfabeto ex: <AAA000>.
  assim conseguimos manter o fluxo de uma forma melhor.

add api para reformulação dos ids de embeds:
  um grande problemas que estamos tendo. é os ids de embed e tickets, se criarmos 1 ambed ele recebe um <id>, mas se apagarmos esse embed não conseguimos usar o id novamente.
  ou seja refatoração de ids.
urile sistema como esse:

import time

class SnowflakeGenerator:
    def __init__(self, machine_id: int = 1):
        self.machine_id = machine_id & 0x3FF  # 10 bits
        self.sequence = 0
        self.last_timestamp = -1
        self.epoch = 1609459200000  # 01/01/2021

    def gerar(self) -> int:
        timestamp = int(time.time() * 1000) - self.epoch
        if timestamp == self.last_timestamp:
            self.sequence = (self.sequence + 1) & 0xFFF
        else:
            self.sequence = 0
        self.last_timestamp = timestamp
        return (timestamp << 22) | (self.machine_id << 12) | self.sequence

snowflake = SnowflakeGenerator(machine_id=1)
novo_id = snowflake.gerar()  # ex: 7294839201847362
