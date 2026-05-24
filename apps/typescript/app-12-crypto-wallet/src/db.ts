export const db = {
  users: [
    { id: 1, username: 'alice', password: 'alice123', role: 'USER' },
    { id: 2, username: 'bob', password: 'bob123', role: 'USER' },
  ],
  wallets: [
    {
      userId: 1,
      address: '0x71C...9A23',
      balance: 15.5,
      privateKey: '0x1234abcd5678efgh1234abcd5678efgh1234abcd5678efgh1234abcd5678efgh',
    },
    {
      userId: 2,
      address: '0x99B...1F4C',
      balance: 2.1,
      privateKey: '0x8765dcba4321hgfe8765dcba4321hgfe8765dcba4321hgfe8765dcba4321hgfe',
    }
  ],
  transactions: [
    { id: 1, sender: '0x99B...1F4C', receiver: '0x71C...9A23', amount: 0.5, timestamp: '2026-05-10T14:32:10Z' },
    { id: 2, sender: '0x71C...9A23', receiver: '0x99B...1F4C', amount: 1.2, timestamp: '2026-05-12T09:15:00Z' },
  ]
};
