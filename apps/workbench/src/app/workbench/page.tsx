import { redirect } from 'next/navigation';

type WorkbenchSearchParams = Promise<{
  region?: string;
  epoch?: string;
  tour?: string;
}>;

export default async function WorkbenchRedirect({
  searchParams,
}: {
  searchParams: WorkbenchSearchParams;
}) {
  const params = await searchParams;
  const zone = params.region === 'amazon' ? 'amazon' : 'mekong';
  const query = new URLSearchParams();
  if (params.epoch) query.set('epoch', params.epoch);
  if (params.tour) query.set('tour', params.tour);
  const suffix = query.toString();

  redirect(`/workbench/${zone}${suffix ? `?${suffix}` : ''}`);
}
