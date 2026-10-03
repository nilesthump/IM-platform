import { accountDatabase } from "../storage/database.js";
import { Repository } from "../../../shared/protocol-sdk/src/storage/repository.js";
import { SendApplication, type Session } from "./send.js";
export async function accountSend(session: Session): Promise<SendApplication> {
  const repository=new Repository(accountDatabase(session.userId));
  await repository.initialize();
  return new SendApplication(repository,session);
}
